import graphene
from graphene_django import DjangoObjectType 
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import ValidationError 
from django.db import transaction 
from django.utils import timezone 
import re
from .models import Customer, Product, Order
from decimal import Decimal
from . filters import CustomerFilter, ProductFilter, OrderFilter

# GraphQL Types for Django Models


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,) # ✅ add this

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,) # ✅ add this

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,) # ✅ add this

class CRMQuery(graphene.ObjectType):
    # Example field
    hello_crm = graphene.String(default_value="Hello from CRM!")
    
# ✅ Define Query here 
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, order_by=graphene.List(of_type=graphene.String))
    all_products = DjangoFilterConnectionField(ProductType, order_by=graphene.List(of_type=graphene.String))
    all_orders = DjangoFilterConnectionField(OrderType, order_by=graphene.List(of_type=graphene.String))

    def resolve_all_customers(root, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_products(root, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_orders(root, info, order_by=None, **kwargs):
        qs = Order.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs


 # ------------------- # CreateCustomer # -------------------

class CreateCustomer(graphene.Mutation): 
    class Arguments: 
        name = graphene.String(required=True) 
        email = graphene.String(required=True) 
        phone = graphene.String(required=False) 
        
    customer = graphene.Field(CustomerType) 
    message = graphene.String() 
    def validate_phone(phone): 
        if phone and not re.match(r"^\+?\d{7,15}$|^\d{3}-\d{3}-\d{4}$", phone): 
            raise ValidationError("Invalid phone format. Use +1234567890 or 123-456-7890.") 
        
    def mutate(self, info, name, email, phone=None): 
        if Customer.objects.filter(email=email).exists(): 
            raise ValidationError("Email already exists.") 
        
        CreateCustomer.validate_phone(phone) 
        
        customer = Customer.objects.create(name=name, email=email, phone=phone) 
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully.") 
    
# BulkCreateCustomers # -------------------
class BulkCreateCustomers(graphene.Mutation): 
        class Arguments: 
            customers = graphene.List(graphene.JSONString, required=True) 
            
        created_customers = graphene.List(CustomerType) 
        errors = graphene.List(graphene.String)
        
        def mutate(self, info, customers):
            created = [] 
            errors = []

            with transaction.atomic():
                for data in customers:
                    try:
                        name = data.get("name")
                        email = data.get("email")
                        phone = data.get("phone")
                        if not name or not email:
                            raise ValidationError("Name and email are required.")
                        if Customer.objects.filter(email=email).exists():
                            raise ValidationError(f"Email {email} already exists.")
                        CreateCustomer.validate_phone(phone)
                        customer = Customer.objects.create(name=name, email=email, phone=phone)
                        created.append(customer)
                    except ValidationError as e:
                        errors.append(str(e))
                return BulkCreateCustomers(created_customers=created, errors=errors)
            
# ------------------- # CreateProduct # -------------------
class CreateProduct(graphene.Mutation): 
    class Arguments: 
        name = graphene.String(required=True) 
        price = graphene.Float(required=True) 
        stock = graphene.Int(required=False) 
        
    product = graphene.Field(ProductType) 
    
    def mutate(self, info, name, price, stock=0): 
        price = Decimal(str(price))
        if price <= 0: 
            raise ValidationError("Price must be positive.") 
        if stock < 0: 
            raise ValidationError("Stock cannot be negative.") 
        
        product = Product.objects.create(name=name, price=price, stock=stock)
        product.save() 
        return CreateProduct(product=product)

# ------------------- # CreateOrder # -------------------
class CreateOrder(graphene.Mutation): 
    class Arguments: 
        customer_id = graphene.Int(required=True) 
        product_ids = graphene.List(graphene.Int, required=True) 
        order_date = graphene.DateTime(required=False) 
        
    order = graphene.Field(OrderType) 
    message = graphene.String() 
    
    def mutate(self, info, customer_id, product_ids, order_date=None): 
        try: 
            customer = Customer.objects.get(id=customer_id) 
        except Customer.DoesNotExist: 
            raise ValidationError("Invalid customer ID.") 
        
        if not product_ids: 
            raise ValidationError("At least one product must be selected.") 
        
        products = Product.objects.filter(id__in=product_ids)
        if products.count() != len(product_ids): 
            raise ValidationError("One or more product IDs are invalid.") 
        
        total_amount = sum([p.price for p in products])
         
        order = Order.objects.create( 
                    customer=customer, 
                    order_date=order_date or timezone.now(), 
                    total_amount=total_amount, )
        order.save() 
        order.products.set(products) 
        
        return CreateOrder(order=order, message="Order created successfully.")
    
# ------------------- # Root Mutation # -------------------
class Mutation(graphene.ObjectType): 
    create_customer = CreateCustomer.Field() 
    bulk_create_customers = BulkCreateCustomers.Field() 
    create_product = CreateProduct.Field() 
    create_order = CreateOrder.Field()
    
    