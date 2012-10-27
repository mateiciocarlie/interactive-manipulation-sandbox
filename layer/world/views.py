from django.http import HttpResponse
from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from layer.world.models import *
from django.contrib.auth.models import User, AnonymousUser
import json

# Create your views here.

def index(request):
    return render_to_response('index.html', {'user': request.user})

def context(request):
    # Get or create Client object associated with this session
    print "Session Key = %s" % request.session.session_key
    # This is a COMPLETE HACK
    # I'm making Ember.data believe that this is a REST API and that
    # the object it is retrieving is a different one per request
    # In order to do that, I send the "client context" (where in the application the user is)
    # as the ID form the client. here I parse it (because ember-data sends it as a REST URL)
    # and I return it as the ID of the "returned Client object"
    # Again, in reality, this ID is simply the context, it is just that in order to
    # make use of this very dirty hack, I have to use it in this way
    id = request.path.split('/')[-1]
    print "Context = %s" % id
    try: 
        client = Client.objects.get(session_key=request.session.session_key)
        print "got existing"
    except Client.DoesNotExist:
        client = Client(session_key=request.session.session_key)
        print "created new"

    # Associate the current logged-in user to the session
    # NOTE: 'username' is the key for the User object so storing
    # this value is enough to retrieve the User object later
    client.username = request.user.username

    # Associate current user context with client object
    client.context = id

    client.save()

    # TODO: Clean-up and remove stale client objects

    # Search and return all other users currently in this context
    others = Client.objects.filter(context=id).exclude(username=client.username)

    other_users = []
    for other in others:
        try:
            other_user = User.objects.get(username=other.username)
            other_users.append(make_user_json( other_user))
        except User.DoesNotExist:
            print "wrong user? username = %s" % other.username
    response_obj = make_user_json( request.user)
    response_obj['id'] = id
    response_obj['other_users'] = other_users
    
    return HttpResponse(json.dumps(response_obj))

def make_user_json( user):
    if type(user) == AnonymousUser:
        return {
            'username': 'AnonymousUser',
            'first_name': '',
            'last_name': 'Anonymous'
        }
    else:
        return {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
            
