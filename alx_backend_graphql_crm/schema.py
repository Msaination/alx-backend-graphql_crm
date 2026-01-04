import graphene

class Query(graphene.ObjectType):
    # Define a simple field
    hello = graphene.String(default_value="Hello, GraphQL!")

# Create the schema object
schema = graphene.Schema(query=Query)
