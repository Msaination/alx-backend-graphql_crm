import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation


class Query(CRMQuery, graphene.ObjectType):
    # Add project-wide fields here
    hello = graphene.String(default_value="Hello, Msiko!")

class Mutation(CRMMutation, graphene.ObjectType):
    # Add project-wide mutations here
    pass


schema = graphene.Schema(query=Query, mutation=CRMMutation)
