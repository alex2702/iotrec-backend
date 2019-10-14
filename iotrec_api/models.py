import math
import uuid as uuid

from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from enumchoicefield import ChoiceEnum, EnumChoiceField
from location_field.models.plain import PlainLocationField
from mptt.fields import TreeForeignKey, TreeManyToManyField
from mptt.models import MPTTModel
from rest_framework.exceptions import ValidationError

from iotrec_api.utils.thing import ThingType


# source: https://steelkiwi.com/blog/practical-application-singleton-design-pattern/
class IotRecSettings(models.Model):
    recommendation_threshold = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(IotRecSettings, self).save(*args, **kwargs)
        self.set_cache()

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                obj.set_cache()
        return cache.get(cls.__name__)

    def set_cache(self):
        cache.set(self.__class__.__name__, self)


class Category(MPTTModel):
    # parent = models.ForeignKey('self', null=True, blank=True, related_name='subcategories', on_delete=models.CASCADE)
    text_id = models.CharField(max_length=255, primary_key=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True,
                            on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_alias = models.BooleanField(default=False)
    alias_owner = TreeForeignKey('self', null=True, blank=True, related_name='target', db_index=True,
                                 on_delete=models.CASCADE)
    #nr_of_items_flat = models.IntegerField(default=0) # TODO maybe use this to make calculations more efficient?
    #nr_of_items_recursive = models.IntegerField(default=0) # TODO maybe use this to make calculations more efficient?

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'Categories'

    # class Meta:
    #    ordering = ('tree_id', 'level')


class User(AbstractUser):
    """DB model for Users"""
    # is_administrator = models.BooleanField(default=False) # TODO remove
    # preferences = TreeManyToManyField('Category', blank=True)


"""
class Venue(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    image = models.ImageField(blank=True)
"""


class ThingManager(models.Manager):
    def get_similarity_of_thing(self, this_thing, other_thing, *args, **kwargs):
        # get all categories that "self" is classified in
        this_thing_categories = this_thing.categories.all()
        this_thing_categories_all = set()
        for i in range(len(this_thing_categories)):
            if this_thing_categories[i] not in this_thing_categories_all:
                this_thing_categories_all.add(this_thing_categories[i])
            i_ancestors = this_thing_categories[i].get_ancestors()
            for j in range(len(i_ancestors)):
                if i_ancestors[j] not in this_thing_categories_all:
                    this_thing_categories_all.add(i_ancestors[j])

        # get all categories that "other" is classified in
        other_thing_categories = other_thing.categories.all()

        other_thing_categories_all = set()
        for i in range(len(other_thing_categories)):
            if other_thing_categories[i] not in other_thing_categories_all:
                other_thing_categories_all.add(other_thing_categories[i])
            i_ancestors = other_thing_categories[i].get_ancestors()
            for j in range(len(i_ancestors)):
                if i_ancestors[j] not in other_thing_categories_all:
                    other_thing_categories_all.add(i_ancestors[j])

        # merge the category lists
        categories_all = this_thing_categories_all.union(other_thing_categories_all)

        divident = 0
        divisor_inner_this = 0
        divisor_inner_other = 0

        # for each category i
        for cat in categories_all:
            # 1 if self has category i, 0 otherwise
            tf_this_i = 1 if (cat in this_thing_categories_all) else 0

            # 1 if other has category i, 0 otherwise
            tf_other_i = 1 if (cat in other_thing_categories_all) else 0

            # number of items classified in subtree for which the parent of i is the root
            # (loop through all descendants of that category, including itself, and add up the things count)
            subtree_root = None
            if cat.is_root_node():
                subtree_root = cat
            else:
                subtree_root = cat.get_ancestors(ascending=True)[0]

            n_p_i = 0
            n_p_i_things_counted = set()  # prevent counting a thing multiple times
            for sub_cat in subtree_root.get_descendants(include_self=True):
                n_p_i += len((set(sub_cat.thing_set.all()) - n_p_i_things_counted))
                n_p_i_things_counted = n_p_i_things_counted.union(set(sub_cat.thing_set.all()))

            # number of items classified in subtree for which i is the root
            # (loop through all descendants of that category, including itself, and add up the things count)
            n_i = 0
            n_i_things_counted = set()  # prevent counting a thing multiple times
            for sub_cat in cat.get_descendants(include_self=True):
                n_i += len((set(sub_cat.thing_set.all()) - n_i_things_counted))
                n_i_things_counted = n_i_things_counted.union(set(sub_cat.thing_set.all()))

            factor_this = tf_this_i * math.log(n_p_i / n_i)
            factor_other = tf_other_i * math.log(n_p_i / n_i)

            divident += factor_this * factor_other
            divisor_inner_this += factor_this * factor_this
            divisor_inner_other += factor_other * factor_other

        result = divident / (math.sqrt(divisor_inner_this) * math.sqrt(divisor_inner_other))

        return result

    def get_similarity_of_user(self, this_thing, user, *args, **kwargs):
        # get all categories that "self" is classified in
        this_thing_categories = this_thing.categories.all()
        this_thing_categories_all = set()
        for i in range(len(this_thing_categories)):
            if this_thing_categories[i] not in this_thing_categories_all:
                this_thing_categories_all.add(this_thing_categories[i])
            i_ancestors = this_thing_categories[i].get_ancestors()
            for j in range(len(i_ancestors)):
                if i_ancestors[j] not in this_thing_categories_all:
                    this_thing_categories_all.add(i_ancestors[j])

        # get all categories that "user" is classified in (from their preferences)
        user_preferences = user.preferences.all()
        user_categories = set()
        for i in user_preferences:
            if i.value != 0:
                user_categories.add(i.category)

        user_categories_all = set()
        for i in user_categories:
            if i not in user_categories_all:
                user_categories_all.add(i)
            i_ancestors = i.get_ancestors()
            for j in range(len(i_ancestors)):
                if i_ancestors[j] not in user_categories_all:
                    user_categories_all.add(i_ancestors[j])

        # merge the category lists
        categories_all = this_thing_categories_all.union(user_categories_all)

        divident = 0
        divisor_inner_this = 0
        divisor_inner_other = 0

        # for each category i
        for cat in categories_all:
            # 1 if self has category i, 0 otherwise
            tf_this_i = 1 if (cat in this_thing_categories_all) else 0

            # 1 or -1 if user has category i, 0 otherwise
            # get frequency of category in user preferences
            if len(user.preferences.filter(category=cat)) > 0 and user.preferences.get(category=cat).value != 0:
                # check if category is directly part of a user preference and if yes, get the value
                tf_user_i = user.preferences.get(category=cat).value
                print(cat)
                print(tf_user_i)
            else:
                # check if a child category is a preference and
                user_prefs_below_cat = set(cat.get_descendants(include_self=False).all()).intersection(user_categories)
                if len(user_prefs_below_cat) > 0:
                    # if yes, build an average of the childrens' preferences values
                    print(str(user_prefs_below_cat))
                    nr_of_user_prefs_below_cat = len(user_prefs_below_cat)
                    values_of_user_prefs_below_cat = 0
                    for i in user_prefs_below_cat:
                        # get the corresponding preference
                        pref = user.preferences.get(category=i)
                        # add up the value
                        values_of_user_prefs_below_cat += pref.value
                    tf_user_i = values_of_user_prefs_below_cat/nr_of_user_prefs_below_cat
                else:
                    tf_user_i = 0

            # this approach is missing tf_user_i for the parents of preferences
            # because parents are not selected in the profile
            # idea: on every category, check if a child category is a preference
            # if yes, build an average of the childrens' preferences values

            # number of items classified in subtree for which the parent of i is the root
            # (loop through all descendants of that category, including itself, and add up the things count)
            subtree_root = None
            if cat.is_root_node():
                subtree_root = cat
            else:
                subtree_root = cat.get_ancestors(ascending=True)[0]
            # if cat.text_id != "Root":
            #    subtree_root = cat.get_ancestors(ascending=True)[0]
            # else:
            #    subtree_root = cat

            n_p_i = 0
            user_flag = 0  # prevent counting the user multiple times
            n_p_i_things_counted = set()  # prevent counting a thing multiple times
            for sub_cat in subtree_root.get_descendants(include_self=True):
                # check if user has that preference
                if sub_cat in user_categories:
                    user_flag = 1
                n_p_i += len((set(sub_cat.thing_set.all()) - n_p_i_things_counted))
                n_p_i_things_counted = n_p_i_things_counted.union(set(sub_cat.thing_set.all()))

            if user_flag == 1:
                n_p_i += 1

            # number of items classified in subtree for which i is the root
            # (loop through all descendants of that category, including itself, and add up the things count)
            n_i = 0
            user_flag = 0  # prevent counting the user multiple times
            n_i_things_counted = set()  # prevent counting a thing multiple times
            for sub_cat in cat.get_descendants(include_self=True):
                # check if user has that preference
                if sub_cat in user_categories:
                    user_flag = 1
                n_i += len((set(sub_cat.thing_set.all()) - n_i_things_counted))
                n_i_things_counted = n_i_things_counted.union(set(sub_cat.thing_set.all()))

            if user_flag == 1:
                n_i += 1

            factor_this = tf_this_i * math.log(n_p_i / n_i)
            factor_other = tf_user_i * math.log(n_p_i / n_i)

            divident += factor_this * factor_other
            divisor_inner_this += factor_this * factor_this
            divisor_inner_other += factor_other * factor_other

        if math.sqrt(divisor_inner_this) * math.sqrt(divisor_inner_other) != 0:
            result = divident / (math.sqrt(divisor_inner_this) * math.sqrt(divisor_inner_other))
        else:
            result = 0

        # normalize to interval [0, 1] (from [-1, 1])
        result = (result + 1)/2

        return result


class Thing(models.Model):
    id = models.CharField(max_length=128, default=None, primary_key=True)
    title = models.CharField(max_length=128, default='New Thing')
    description = models.TextField(blank=True)
    type = EnumChoiceField(ThingType, default=ThingType.BCN_I)
    uuid = models.UUIDField(default=uuid.uuid4)
    major_id = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(65535)], default=0)
    minor_id = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(65535)], default=0)
    image = models.ImageField(blank=True)
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    location = PlainLocationField(based_fields=['address'], blank=True)
    categories = TreeManyToManyField('Category', blank=True)
    objects = ThingManager()

    def save(self, *args, **kwargs):
        print(str(self.pk))
        if not self.pk:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()

        self.id = '{0}-{1}-{2}'.format(self.uuid, self.major_id, self.minor_id)

        '''
        # go through all categories of this thing
            # cycle through 
        for cat in self.categories:
            Thing.objects.all
        '''

        try:
            self.full_clean()
        except ValidationError as e:
            pass

        super(Thing, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    # def calculate_similarity(self, other):

    # def clean_id(self):
    #    return '{0}-{1}-{2}'.format(self.uuid, self.major_id, self.minor_id)


class Recommendation(models.Model):
    id = models.UUIDField(default=None, primary_key=True, editable=False)
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    thing = models.ForeignKey("Thing", on_delete=models.CASCADE)
    invoke_rec = models.BooleanField(editable=False, default=False)
    score = models.FloatField(editable=False, default=0)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = uuid.uuid4()
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        self.score = Thing.objects.get_similarity_of_user(self.thing, self.user)
        self.invoke_rec = self.get_invoke_rec(self.score)
        super(Recommendation, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)

    def get_invoke_rec(self, score, *args, **kwargs):
        settings = IotRecSettings.load()
        return score > settings.recommendation_threshold


class Feedback(models.Model):
    id = models.UUIDField(default=None, primary_key=True, editable=False)
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    recommendation = models.ForeignKey("Recommendation", on_delete=models.CASCADE)
    value = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = uuid.uuid4()
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(Feedback, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class Preference(models.Model):
    VALUE_CHOICES = [
        (-1, '-1'),
        (1, '1'),
    ]

    #id = models.UUIDField(default=None, primary_key=True, editable=False)
    id = models.CharField(max_length=255, primary_key=True, editable=False)
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    category = TreeForeignKey("Category", on_delete=models.CASCADE)
    value = models.IntegerField(choices=VALUE_CHOICES, default=0)
    user = models.ForeignKey("User", related_name="preferences", on_delete=models.CASCADE)

    def validate_unique(self, exclude=None):
        # get all preferences of the given user
        user_prefs = Preference.objects.filter(user=self.user)
        # reject new preference if user has it already
        if user_prefs.filter(category=self.category).exists():
            raise ValidationError('User already has that preference')

    def save(self, *args, **kwargs):
        #self.validate_unique()
        if not self.pk:
            #self.pk = uuid.uuid4()
            self.pk = self.category.text_id
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(Preference, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.category) + " (" + str(self.value) + ")"
