
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


from django.http import FileResponse
from django.http import QueryDict
from django.views import View
from django.http import JsonResponse
from api.models import *
from api.models import Files as Files
from api import utils
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class HelloView(View):

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return JsonResponse(content)


@method_decorator(csrf_exempt, name='dispatch')
class UserView(View):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        identifier = request.GET.get('identifier')
        if identifier == None:
            content = utils.the_matrix()
            content = {'message': 'success', 'data': content}
            return JsonResponse(content)
        content = Project.objects.get(identifier=identifier).serialize()
        return JsonResponse(content)

    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        user = User(email=body['username'],
                    password=body['password'], role=body['role'])
        user.create()
        content = {'message': 'user created', 'error': False}
        return JsonResponse(content)


@method_decorator(csrf_exempt, name='dispatch')
class SessionView(View):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        identifier = request.GET.get('identifier')
        if identifier == None:
            content = utils.the_matrix()
            content = {'message': 'success', 'data': content}
            return JsonResponse(content)
        content = Project.objects.get(identifier=identifier).serialize()
        return JsonResponse(content)

    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        session = Session().login(body['username'], body['password'])
        content = {'message': session[0], 'status': session[1],
                   'role': session[2], 'token': session[3]}
        return JsonResponse(content)


@method_decorator(csrf_exempt, name='dispatch')
class ProjectView(View):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        identifier = request.GET.get('identifier')
        if identifier == None:
            content = utils.the_matrix()
            content = {'message': 'success', 'data': content}
            return JsonResponse(content)
        content = Project.objects.get(identifier=identifier).serialize()
        return JsonResponse(content)

    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        project = Project()
        project.create(body)
        content = {'message': 'Proyecto creado', 'error': False}
        return JsonResponse(content)


@method_decorator(csrf_exempt, name='dispatch')
class ProductView(View):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        product = Product.objects.get(identifier=request.GET.get('identifier'))
        content = product.get_view()
        print(content)
        return JsonResponse(content)

    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        node = None
        if 'referenceType' not in body:
            pass
        elif body['referenceType'] == "step":
            step = ProductStep.objects.get(identifier=body['reference_id'])
            node = Node.objects.get(product_step=step)
        elif body['referenceType'] == "product":
            product_preview = Product.objects.get(
                identifier=body['reference_id'])
            node = Node.objects.get(product=product_preview)
        product = Node()
        product = product.create(body, "product", node)
        content = {'message': 'Producto creado',
                   'error': False, 'node': product.identifier}
        return JsonResponse(content)


@method_decorator(csrf_exempt, name='dispatch')
class ProjectGraph(View):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        content = utils.get_graph(1)
        return JsonResponse(content)


@method_decorator(csrf_exempt, name='dispatch')
class ProductStepView(View):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        identifier = request.GET.get('identifier')
        step = ProductStep.objects.get(identifier=identifier).serialize()
        content = {'data': step, 'error': False}
        return JsonResponse(content)

    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        node = None
        if 'referenceType' not in body:
            pass
        elif body['referenceType'] == "step":
            step = ProductStep.objects.get(identifier=body['reference_id'])
            node = Node.objects.get(product_step=step)
        elif body['referenceType'] == "product":
            product_preview = Product.objects.get(
                identifier=body['reference_id'])
            node = Node.objects.get(product=product_preview)
        product = Node()
        product = product.create(body, "step", node)
        content = {'message': 'Etapa creada',
                   'error': False, 'node': product.identifier}
        return JsonResponse(content)


@api_view(['GET', 'PUT'])
def FilesView(request):
    if request.method == 'GET':
        import os
        file_name = request.GET.get('file_name')
        file_ = open(os.path.join(os.getcwd(), file_name), 'rb')
        response = FileResponse(file_)
        return response

    elif request.method == 'PUT':
        file_ = request.data.get('file')
        type_ = request.data.get('type_')
        file_name = request.data.get('file_name')
        identifier = request.data.get('identifier')

        if type_ == 'project':
            new_file = Files(file_attach=file_, project=Project.objects.get(
                identifier=identifier), file_name=file_name)
            new_file.save()
        elif type_ == 'step':
            new_file = Files(file_attach=file_, product_step=ProductStep.objects.get(
                identifier=identifier), file_name=file_name)
            new_file.save()
        elif type_ == 'product':
            new_file = Files(file_attach=file_, product=Product.objects.get(
                identifier=identifier), file_name=file_name)
            new_file.save()
        content = {'message': 'Etapa creada', 'error': False}
        return JsonResponse(content)


@api_view(['GET', 'PUT'])
def AssignmentDeliveryView(request):
    if request.method == 'GET':
        if request.GET.get('check') == "1":
            type_ = request.GET.get('type_')
            identifier = request.GET.get('identifier')
            user = Session().get_user(
                request.headers['Authorization'].split(' ')[1])
            delivery = None
            if type_ == 'project':
                delivery = AssignmentDelivery.objects.filter(
                    project=Project.objects.get(identifier=identifier), user=user).first()
            elif type_ == 'step':
                delivery = AssignmentDelivery.objects.filter(
                    product_step=ProductStep.objects.get(identifier=identifier), user=user).first()
            elif type_ == 'product':
                delivery = AssignmentDelivery.objects.filter(
                    product=Product.objects.get(identifier=identifier), user=user).first()

            content = {'message': delivery != None, 'error': False}
            if delivery != None:
                content = {'message': delivery != None, 'error': False,
                           "identifier": delivery.identifier, 'date':  delivery.delivery_date}
            return JsonResponse(content)

        else:
            import os
            file_name = request.GET.get('identifier')
            delivery = AssignmentDelivery.objects.get(
                identifier=file_name).file_attach
            #file_ = open(os.path.join(os.getcwd(), delivery.file_attach), 'rb')
            response = FileResponse(delivery)
            return response

    elif request.method == 'PUT':
        import datetime
        file_ = request.data.get('file')
        type_ = request.data.get('type_')
        file_name = request.data.get('file_name')
        identifier = request.data.get('identifier')
        user = Session().get_user(
            request.headers['Authorization'].split(' ')[1])
        if type_ == 'project':
            exist = AssignmentDelivery.objects.filter(project=Project.objects.get(
                identifier=identifier), user=user).first()
            if exist == None:
                new_file = AssignmentDelivery(file_attach=file_, project=Project.objects.get(
                    identifier=identifier), file_name=file_name, user=user)
                new_file.save()
            else:
                exist.file_attach = file_
                exist.delivery_date = datetime.datetime.now()
                exist.save()
        elif type_ == 'step':
            exist = AssignmentDelivery.objects.filter(product_step=ProductStep.objects.get(
                identifier=identifier), user=user).first()
            if exist == None:
                new_file = AssignmentDelivery(file_attach=file_, product_step=ProductStep.objects.get(
                    identifier=identifier), file_name=file_name, user=user)
                new_file.save()
            else:
                exist.file_attach = file_
                exist.delivery_date = datetime.datetime.now()
                exist.save()
        elif type_ == 'product':
            exist = AssignmentDelivery.objects.filter(product=Product.objects.get(
                identifier=identifier), user=user).first()
            if exist == None:
                new_file = AssignmentDelivery(file_attach=file_, product=Product.objects.get(
                    identifier=identifier), file_name=file_name, user=user)
                new_file.save()
            else:
                exist.file_attach = file_
                exist.delivery_date = datetime.datetime.now()
                exist.save()
        content = {'message': 'Etapa creada', 'error': False}
        return JsonResponse(content)
