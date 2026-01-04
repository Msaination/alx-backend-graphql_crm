import graphene

class CRMQuery(graphene.ObjectType):
    # Example field
    hello_crm = graphene.String(default_value="Hello from CRM!")
