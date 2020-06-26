from flask import Flask
from flask_cors import CORS
from flask_restx import Api, Resource, fields

from ListAdministration import Administration
from ListAdministration import StatisticAdministration
from bo.Group import Group
from bo.User import User
from bo.Article import Article
from bo.ShoppingList import ShoppingList

app = Flask(__name__)

"""Flask-Erweiterung für Cross-Origin Resource Sharing"""
CORS(app, resources=r'/app/*')

api = Api(app, version='1.0', title='HOLMA API',
          description='Eine rudimentäre Demo-API für Listenerstellung.')

"""Namespaces"""
holmaApp = api.namespace('app', description="Funktionen der App")

bo = api.model('BusinessObject', {
    'name': fields.String(attribute='_name', description='Name eines Objekts'),
    'id': fields.Integer(attribute='_id',
                         description='Der Unique Identifier eines Business Object'),
    'creationDate': fields.Date(attribute='_creation_date',
                                description='Erstellungsdatum des BOs, wird durch Unix Time Stamp ermittlet'),
    'lastUpdated': fields.Date(attribute='_last_updated',
                               description='Änderungsdatum des BOs, wird durch Unix Time Stamp ermittlet')
})

user = api.inherit('User', bo, {
    'email': fields.String(attribute='_email',
                           description='E-Mail-Adresse eines Benutzers'),
    'googleId': fields.String(attribute='_google_id',
                              description='google id eines Benutzers'),
})

group = api.inherit('Group', bo, {
    'owner': fields.Integer(attribute='_owner',
                            description='Unique Id des Gruppeninhabers'),
})

shoppingList = api.inherit('ShoppingList', bo, {
    'group': fields.Integer(attribute='_group',
                            description='ID der Gruppe zu der diese Liste gehört'),
})

listEntry = api.inherit('ListEntry', bo, {
    'article': fields.Integer(attribute='_article',
                              description='zu welchem Artikle gehört dieses Entry? '),
    'amount': fields.Float(attribute='_amount',
                           description='Menge des Entries '),
    'unit': fields.String(attribute='_unit',
                          description='Einheit des Entries '),
    'purchasingUser': fields.String(attribute='_purchasing_user',
                                    description='Wer das Artikle kaufen muss '),
    'shoppingList': fields.Integer(attribute='_Shopping_list',
                                   description='zu welcher Liste diese Entry gehört?'),
    'retailer': fields.String(attribute='_retailer',
                              description='Bei wem das Artikle gekauft  '),
    'checked': fields.Boolean(attribute='_checked',
                              description='wurde es bereits gekauft'),
    'checkedTs': fields.DateTime(attribute='_checked_ts',
                                 description='wann wurde es gekauft'),
    'standardarticle': fields.Boolean(attribute='_standardarticle',
                                      description='ist es ein Standardartikle')
})

article = api.inherit('Article', bo, {
    'group': fields.Integer(attribute='_group',
                            description='zu welcher Groupe dieses Artikle gehört?'),
})

retailer = api.inherit('Retailer', bo)


@holmaApp.route('/users')
@holmaApp.response(500, 'Falls es zu einem Server -seitigen Fehler kommt')
class UserListOperations(Resource):
    @holmaApp.marshal_list_with(user)
    # @secured
    def get(self):
        adm = Administration()
        user_list = adm.get_all_users()
        return user_list

    @holmaApp.marshal_with(user, code=200)
    @holmaApp.expect(user)  # Wir erwarten ein USer-Objekt von Client-Seite.
    # @secured
    def post(self):
        adm = Administration()
        proposal = User.from_dict(api.payload)
        if proposal is not None:
            usr = adm.create_user(proposal.get_name(), proposal.get_email(),
                                  proposal.get_google_id())
            return usr, 200
        else:
            return '', 500


@holmaApp.route('/users/<int:user_id>')
@holmaApp.response(500, 'Falls es zu einem Server-seitigen Fehler kommt.')
@holmaApp.param('user_id', 'Die ID des User-Objekts')
class UserOperations(Resource):
    @holmaApp.marshal_with(user)
    # @secured
    def get(self, user_id):

        adm = Administration()
        usr = adm.get_user_by_id(user_id)
        return usr

    # @secured
    def delete(self, user_id):

        adm = Administration()
        usr = adm.get_user_by_id(user_id)
        if usr is not None:
            adm.delete_user(usr)
            return '', 200
        else:
            return '', 500

    @holmaApp.marshal_with(user)
    @holmaApp.expect(user, validate=True)
    # @secured
    def put(self, user_id):
        adm = Administration()
        usr = User.from_dict(api.payload)

        if usr is not None:
            usr.set_id(user_id)
            adm.save_user(usr)
            return '', 200
        else:
            return '', 500


@holmaApp.route('/users/by-google-id/<string:google_id>')
@holmaApp.response(500, 'Falls es zu einem Server-seitigen Fehler kommt.')
@holmaApp.param('google_id', 'Die ID des User-Objekts')
class UserByGoogleIdOperation(Resource):
    @holmaApp.marshal_with(user)
    # @secured
    def get(self, google_id):

        adm = Administration()
        usr = adm.get_user_by_google_id(google_id)
        return usr


@holmaApp.route('/users/by-name/<string:name>')
@holmaApp.response(500, 'Falls es zu einem Server-seitigen Fehler kommt.')
@holmaApp.param('name', 'Der Name des Users')
class UserByNameOperations(Resource):
    @holmaApp.marshal_with(user)
    # @secured
    def get(self, name):
        adm = Administration()
        us = adm.get_user_by_name(name)
        return us


@holmaApp.route('/groups')
@holmaApp.response(500, 'Falls es zu einem Server-seitigem Fehler kommt.')
class GroupListOperations(Resource):
    @holmaApp.marshal_list_with(group)
    # @secured
    def get(self):
        adm = Administration()
        group_list = adm.get_all_groups()
        return group_list


@holmaApp.route('/groups/<int:group_id>')
@holmaApp.response(500, 'Falls es zu einem Server-seitigen Fehler kommt.')
@holmaApp.param('group_id', 'Die ID des Group-Objekts')
class GroupOperations(Resource):
    @holmaApp.marshal_with(group)
    # @secured
    def get(self, group_id):

        adm = Administration()
        grp = adm.get_group_by_id(group_id)
        return grp

    # @secured
    def delete(self, group_id):

        adm = Administration()
        grp = adm.get_group_by_id(group_id)
        if grp is not None:
            adm.delete_group(grp)
            return '', 200
        else:
            return '', 500

    @holmaApp.marshal_with(group)
    @holmaApp.expect(group, validate=True)
    # @secured
    def put(self, group_id):
        adm = Administration()
        grp = Group.from_dict(api.payload)

        if grp is not None:
            grp.set_id(group_id)
            adm.save_group(grp)
            return '', 200
        else:
            return '', 500


@holmaApp.route('/groups/by-name/<string:name>')
@holmaApp.response(500, 'Falls es zu einem Server-seitigen Fehler kommt.')
@holmaApp.param('name', 'Der Name der Gruppe')
class GroupsByNameOperations(Resource):
    @holmaApp.marshal_with(group)
    # @secured
    def get(self, name):
        adm = Administration()
        us = adm.get_groups_by_name(name)
        return us


@holmaApp.route('/users/<int:user_id>/groups')
@holmaApp.response(500, 'Falls es zu einem Server-seitigen Fehler kommt.')
@holmaApp.param('user_id', 'Die ID des User-Objekts')
class UserRelatedGroupOperations(Resource):
    @holmaApp.marshal_with(group)
    # @secured
    def get(self, user_id):

        adm = Administration()
        us = adm.get_user_by_id(user_id)

        if us is not None:
            group_list = adm.get_groups_by_user_id(user_id)
            return group_list
        else:
            return "User not found", 500

    @holmaApp.marshal_with(group, code=201)
    # @secured
    def post(self, user_id):
        adm = Administration()
        us = adm.get_user_by_id(user_id)
        proposal = Group.from_dict(api.payload)

        if us is not None and proposal is not None:
            result = adm.create_group(proposal.get_name(), user_id)
            return result
        else:
            return "User unkown or payload not valid", 500


# Neu

@holmaApp.route('/group/<int:group_id>/users')
@holmaApp.response(500, 'Falls es zu einem Server-seitigen Fehler kommt.')
@holmaApp.param('group_id', 'Die ID des Group-Objekts')
class GroupRelatedUserOperations(Resource):
    @holmaApp.marshal_with(user)
    # @secured
    def get(self, group_id):
        # objekt nicht benötigt, nur group ID
        adm = Administration()
        grp = adm.get_group_by_id(group_id)

        if grp is not None:
            user_list = adm.get_members_by_group_id(group_id)
            return user_list
        else:
            return "Group not found", 500


@holmaApp.route('/group/<int:group_id>/user/<int:user_id>')
@holmaApp.response(500, 'Falls es zu einem Server-seitigen Fehler kommt.')
@holmaApp.param('group_id', 'Die ID des Group-Objekts')
@holmaApp.param('user_id', 'Die ID des User-Objekts')
class GroupUserRelationOperations(Resource):
    @holmaApp.marshal_with(user)
    @holmaApp.marshal_with(group)
    # @secured
    def post(self, group_id, user_id):
        adm = Administration()
        grp = adm.get_group_by_id(group_id)
        us = adm.get_user_by_id(user_id)

        if grp is not None and us is not None:
            result = adm.add_member_to_group(grp, us)
            return result
        else:
            return "Group or User not found", 500

    def delete(self, group_id, user_id):
        adm = Administration()
        grp = adm.get_group_by_id(group_id)
        us = adm.get_user_by_id(user_id)

        if grp is not None and us is not None:
            result = adm.remove_member_from_group(grp, us)
            return result
        else:
            return "Group or User not found", 500


"""@holmaApp.route('/articles')
@holmaApp.response(500,'Falls es zu einem Server-seitigem Fehler kommt.')
class ArticleListOperations(Resource):
    @holmaApp.marshal_list_with(article)
    # @secured
    def get(self):
        adm = StatisticAdministration()
        art = adm.get_all_articles()
        return art


@holmaApp.route('/articles/<int:id>')
@holmaApp.response(500,'Falls es zu einem Server-seitigen Fehler kommt.')
@holmaApp('id', 'Die ID des article-Objekts')
class ArticleOperations(Resource):
    @holmaApp.marshal_with(article)
    # @secured
    def get(self, article_id):

        adm = Administration()
        art = adm.get_article_by_id(article_id)
        return art

    # @secured
    def delete(self, article_id):

        adm = Administration()
        art = adm.get_article_by_id(article_id)
        adm.delete_article(art)
        return '', 200

    @holmaApp.marshal_with(article)
    @holmaApp.expect(article, validate=True)
    # @secured
    def post(self, article_id):
        adm = Administration()
        art = Group.from_dict(api.payload)

        if art is not None:
            art.set_id(article_id)
            adm.save_group(art)
            return '', 200
        else:
            return '', 500


@holmaApp.route('/articles/by-name/<string:name>')
@holmaApp.response(500, 'Falls es zu einem Server-seitigen Fehler kommt.')
@holmaApp.param('name', 'Der Name des Articles')
class ArticlesByNameOperations(Resource):
    @holmaApp.marshal_list_with(article)
    # @secured
    def get(self, name):
        adm = Administration()
        us = adm.get_article_by_name(name)
        return us


@holmaApp.route('/groups/<int:id>/articles')
@holmaApp.response(500, 'Falls es zu einem Server-seitigen Fehler kommt.')
@holmaApp.param('id', 'Die ID des person-Objekts')
class GroupRelatedArticleOperations(Resource):
    @holmaApp.marshal_with(article)
    # @secured
    def get(self, group_id):

        adm = Administration()
        grp = adm.get_group_by_id(group_id)

        if grp is not None:
            # Jetzt erst lesen wir die Konten des Customer aus.
            articles_list = adm.get_articles_by_group_id(grp)
            return articles_list
        else:
            return "No articles found", 500

    @holmaApp.marshal_with(article, code=201)
    # @secured
    def post(self, group_id):
        adm = Administration()
        art = adm.get_group_by_id(group_id)

        proposal = Article.from_dict(api.payload)

        if art is not None and proposal is not None:
            result = adm.create_group(proposal.get_name(), group_id)
            return result
        else:
            return "Group unkown or payload not valid", 500


@holmaApp.route('/groups/<int:group_id>/shoppinglists')
@holmaApp.response(500, 'Falls es zu einem Server-seitigen Fehler kommt.')
@holmaApp.param('group_id', 'Die ID des group-Objekts')
class GroupRelatedShoppingListOperations(Resource):
    @holmaApp.marshal_with(shoppingList)
    #@ secured
    def get(self, group_id):
        adm = Administration()
        sl = adm.get_group_by_id(group_id)
        if sl is not None:
            shoppinglists_list = adm.get_shopping_lists_by_group_id(sl)
            return shoppinglists_list
        else:
            return "Group not found", 500

    @holmaApp.marshal_with(shoppingList, code=201)
    #@ secured
    def post(self, group_id):
        adm = Administration()
        sl = adm.get_group_by_id(group_id)
        proposal = ShoppingList.from_dict(api.payload)

        if sl is not None and proposal is not None:
            result = adm.create_shopping_list(proposal.get_name(), group_id)
            return result
        else:
            return "Group unkown or payload not valid", 500


@holmaApp.route('/shoppinglists/<int:shopping_list_id>')
@holmaApp.response(500, 'Falls es zu einem Server-seitigen Fehler kommt.')
@holmaApp.param('shoppinglist_id', 'Die ID des Shopping-List-Objekts')
class ShoppingListOperations(Resource):
    @holmaApp.marshal_with(group)
    # @secured
    def get(self, shopping_list_id):

        adm = Administration()
        sl = adm.get_shopping_list_by_id(shopping_list_id)
        return sl

    # @secured
    def delete(self, shopping_list_id):

        adm = Administration()
        sl = adm.get_shopping_list_by_id(shopping_list_id)
        if sl is not None:
            adm.delete_group(sl)
            return '', 200
        else:
            return '', 500
"""

if __name__ == '__main__':
    app.run(debug=True)
