when saving a model that is like nested inside another model, we generally use like nested structure to save the model instance into the database

the model instance that is saved into the database is like in the following format:

user.phone.save()

so we use the dot syntax to like save the data into the database

user.phone.save()

this is what is used to save the model instance into the database.

exceptions are DRF features.

they help raise exception itself when certain criteria don't meet.

RegisterSerializer is inheriting from serializers.Serializer

generally validators are put and kept in the serializers class itself so

Generally we call the validate method and access the incoming data from it as

```
validated_data.get()
```

RegisterSerializer provides a custom signup method.

we override that method to add extra functionality

---

For Registration we use the following fields:

1. firstname
2. lastname
3. phone num or email (either one has to be present)
4. password
5. conf password

firstname and lastname are write only -->not sent in response.

style={"input_type":"password"}

this is written so that the password is not shown

```
            queryset=User.objects.get(phone__phone_number=value)
```

the syntax in get is specific to django ORM with model and field name.

this type of syntax is used when from the user we try to check if the phone_number is valid.

like from User.phone.phone_number -->similar to js

if it is in same model:

```
        phone_number_qs=PhoneNumber.objects.get(phone_number=phone_number)

```

directly from PhoneNumber model

```
    user=serializers.CharField(source="user.get_full_name",read_only=True)
```

instead of just returning the pk of the user we return the name

```
    user=serializers.HiddenField(default=serializers.CurrentUserDefault())
```

serializers.HiddenField --> used to represent fields that should be hidden when serializing data, meaning they won't be included in the response sent to the client.

default=serializers.CurrentUserDefault() utility that sets the value of the field to the current authenticated user. If no user is authenticated, it sets the value to None.

allauth is a package that provides the entire auth package in django

```
        serializer=self.get_serializer(data=request.data)

```

will give the respective serializer class used in the view.

as_view() --> this is like calling the api endpoint as an endpoint itself.

get_object --> this is also a method that can be overwritten in views to return user.

task:

1. modify the phone number to accomodate OTPs
2. one user -->many otps
3. modifiy the user object to have phone number field. the username field should behave like phone number.

Signal works in such a way that if certain event has happened then it will automatically get fired.

This will allow the profile to be created once the user has already registered.

this is a great way for logging the users and sending them the required information.
