from datetime import datetime

from bo.Group import Group
from bo.ListEntry import ListEntry
from bo.ShoppingList import ShoppingList
from bo.User import User
from bo.Article import Article
from db.ArticleMapper import ArticleMapper
from db.GroupMapper import GroupMapper
from db.ListEntryMapper import ListEntryMapper
from db.RetailerMapper import RetailerMapper
from db.ShoppingListMapper import ShoppingListMapper
from db.UserGroupRelationsMapper import UserGroupRelationsMapper
from db.UserMapper import UserMapper


class Administration():
    """User"""

    def get_all_users(self):
        with UserMapper() as mapper:
            return mapper.find_all()

    def get_user_by_name(self, name):
        with UserMapper() as mapper:
            return mapper.find_by_name(name)

    def get_user_by_id(self, user_id):
        with UserMapper() as mapper:
            return mapper.find_by_id(user_id)

    def get_user_by_google_id(self, google_id):
        with UserMapper() as mapper:
            return mapper.find_by_google_id(google_id)

    def get_groups_by_user_id(self, user_id):
        with UserGroupRelationsMapper() as mapper:
            return mapper.find_groups_by_user_id(user_id)

    def get_list_entries_by_user_id(self, user_id):
        with ListEntryMapper() as mapper:
            return mapper.find_by_purchasing_user(user_id)

    def create_user(self, name, email, google_id):
        user = User()
        user.set_id(0)
        user.set_name(name)
        user.set_email(email)
        user.set_google_id(google_id)
        with UserMapper() as mapper:
            mapper.insert(user)

    def delete_user(self, user):
        with UserGroupRelationsMapper() as mapper:
            mapper.delete_user_relations(user)

        with UserMapper() as mapper:
            mapper.delete(user)

    def save_user(self, user):
        user.set_last_updated(datetime.now())
        with UserMapper() as mapper:
            mapper.update(user)

    """Gruppe"""

    def get_all_groups(self):
        with GroupMapper() as mapper:
            return mapper.find_all()

    def get_group_by_id(self, group_id):
        with GroupMapper() as mapper:
            return mapper.find_by_id(group_id)

    def get_groups_by_name(self, name):
        with GroupMapper() as mapper:
            return mapper.find_by_name(name)

    def get_members_by_group_id(self, group_id):
        with UserGroupRelationsMapper() as mapper:
            return mapper.find_users_by_group_id(group_id)

    def get_articles_by_group_id(self, group_id):
        with ArticleMapper() as mapper:
            return mapper.find_by_group(group_id)

    def get_shopping_lists_by_group_id(self, group_id):
        with ShoppingListMapper() as mapper:
            return mapper.find_by_group(group_id)

    """def get_standardarticles_by_group_id(self, group_id):
        pass"""

    def add_member_to_group(self, group, user):
        with UserGroupRelationsMapper() as mapper:
            mapper.add_user_to_group(group, user)

    def remove_member_from_group(self, group, user):
        with UserGroupRelationsMapper() as mapper:
            mapper.remove_user_from_group(group, user)

    """def add_standardarticle_to_group(self, group, list_entry):
        with ListEntryMapper() as mapper:
            mapper."""

    """def remove_standardarticle_from_group(self, group, list_entry):
        with ListEntryMapper() as mapper:
            mapper."""

    def create_group(self, name, user_id):
        group = Group()
        group.set_id(0)
        group.set_name(name)
        group.set_owner(user_id)
        with GroupMapper() as mapper:
            return mapper.insert(group)

    def delete_group(self, group):
        with UserGroupRelationsMapper() as mapper:
            mapper.delete_group_relations(group)

        with GroupMapper() as mapper:
            mapper.delete(group)

    def save_group(self, group):
        group.set_last_updated(datetime.now())
        with GroupMapper() as mapper:
            mapper.update(group)

    """eventuell reichen die delete-methoden der objekte selbst

    def add_article_to_group(self, group, article):
        pass

    def remove_article_from_group(self, group, article):
        pass

    def remove_shopping_list_from_group(self, group, shopping_list):
        pass"""



    """Artikel"""

    def get_article_by_id(self, article_id):
        with ArticleMapper() as mapper:
            mapper.find_by_id(article_id)

    def get_article_by_name(self, name):
        with ArticleMapper() as mapper:
            mapper.find_by_name(name)

    def create_article(self, name, group_id):
        article = Article()
        article.set_id(0),
        article.set_name(name),
        article.set_group(group_id)
        with ArticleMapper() as mapper:
            mapper.insert(article)

    def delete_article(self, article):
        with ArticleMapper as mapper:
            mapper.delete(article)

    def save_article(self, article):
        with ArticleMapper as mapper:
            mapper.update(article)

    """Listentry"""

    def get_all_list_entries(self):
        with ListEntryMapper() as mapper:
            mapper.find_all()

    def get_list_entry_by_id(self, list_entry_id):
        with ListEntryMapper() as mapper:
            mapper.find_by_id(list_entry_id)

    def create_list_entry(self, name, article_id, amount, unit, retailer_id,
                          user_id, shopping_list_id):
        listentry = ListEntry()
        listentry.set_id(0),
        listentry.set_name(name),
        listentry.set_purchasing_user(user_id),
        listentry.set_amount(amount),
        listentry.set_article(article_id),
        listentry.set_unit(unit),
        listentry.set_retailer(retailer_id),
        listentry.set_shopping_list(shopping_list_id)
        with ListEntryMapper() as mapper:
            mapper.insert(listentry)

        with ListEntryMapper() as mapper:
            mapper.insert()

    def delete_list_entry(self, list_entry):
        with ListEntryMapper() as mapper:
            mapper.delete(list_entry)

    def save_list_entry(self, list_entry):
        with ListEntryMapper() as mapper:
            mapper.update(list_entry)

    """Einkaufsliste"""

    def get_shopping_list_by_id(self, shopping_list_id):
        with ShoppingListMapper as mapper:
            mapper.find_by_id(shopping_list_id)

    def get_shopping_list_by_name(self, name):
        with ShoppingListMapper as mapper:
            mapper.find_by_name(name)

    def get_list_entries_by_shopping_list_id(self, shoppinglist_id):
        with ListEntryMapper as mapper:
            mapper.find_list_entries_by_shopping_list(shoppinglist_id)

    """Für was die Schleife?"""
    def get_list_entries_checked_by_shopping_list_id(self, shopping_list_id):
        list_entries_checked = []
        list_entries = self.get_list_entries_by_shopping_list_id(
            shopping_list_id)
        for list_entry in list_entries:
            if list_entry.is_checked():
                list_entries_checked.append(list_entry)
        return list_entries_checked

    def create_shopping_list(self, name, group_id):
        shopping_list = ShoppingList()
        shopping_list.set_id(1)
        shopping_list.set_name(name)
        shopping_list.set_group(group_id)
        with ShoppingListMapper as mapper:
            mapper.insert(shopping_list)

    def delete_shopping_list(self, shopping_list):
        with ShoppingListMapper as mapper:
            mapper.delete(shopping_list)

    def save_shopping_list(self, shopping_list):
        with ShoppingListMapper as mapper:
            mapper.update(shopping_list)

    """Retailer"""

    def get_all_retailers(self):
        with RetailerMapper as mapper:
            mapper.find_all()

    def get_retailer_by_id(self, retailer_id):
        with RetailerMapper as mapper:
            mapper.find_by_id(retailer_id)

    def get_retailers_by_name(self, name):
        with RetailerMapper as mapper:
            mapper.find_by_name(name)

    """Statistik Client"""

class StatisticAdministration(object):
    def __init__(self):
        pass

    def get_all_articles(self):
        with ArticleMapper as mapper:
            mapper.find_all()

    def get_all_list_entries(self):
        with ListEntryMapper as mapper:
            mapper.find_all()

    def get_list_entries_by_retailer_id(self, retailer_id):
        with ListEntryMapper as mapper:
            mapper.find_by_retailer(retailer_id)

    def get_list_entries_in_time_period(self, start_date, end_date):
        pass

    def get_list_entries_by_article_id(self, article_id):
        with ListEntryMapper as mapper:
            mapper.find_list_entries_by_article(article_id)
