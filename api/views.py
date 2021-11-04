
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


from django.http import FileResponse
from django.http import HttpResponse
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
        role = request.GET.get('role')
        users = UserProfile().get_all_by_role(role)
        content = {'message': 'users', 'error': False, 'data': users}
        return JsonResponse(content)

    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        user = User(email=body['email'],
                    password=body['password'], role=body['role'])
        user.create()
        user_profile = UserProfile(
            user=user, rut=body['rut'], name=body['name'], last_name=body['last_name'])
        user_profile.save()
        content = {'message': 'user created' + body['email'], 'error': False}
        return JsonResponse(content)


@method_decorator(csrf_exempt, name='dispatch')
class GroupView(View):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        project = Project.objects.get(identifier=request.GET.get('identifier'))
        return_groups = utils.get_groups_by_project(project)
        content = {'message': 'user created',
                   'data': list(reversed(return_groups)), 'error': False}
        return JsonResponse(content)

    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        project = Project.objects.get(identifier=body['identifier'])
        group = Group(project=project, name=body['name'])
        group.save()
        content = {'message': 'group created' + body['name'], 'error': False}
        return JsonResponse(content)


@method_decorator(csrf_exempt, name='dispatch')
class UserGroupView(View):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        action = request.GET.get('action')
        if action == 'free':
            project_id = request.GET.get('project_id')
            project = Project.objects.filter(identifier=project_id).first()
            user_data = UserGroup().get_users_not_in_groups_by_project(project)
            content = {'message': 'success', 'data': user_data}
            return JsonResponse(content)
        else:
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
        user = User.objects.get(email=body['email'])
        group = Group.objects.get(identifier=body['identifier'])
        user_group = UserGroup(user=user, group=group)
        user_group.save()
        content = {'message': 'user group created ' + datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S'), 'error': False}
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
        user = Session().get_user(
            request.headers['Authorization'].split(' ')[1])
        if user.role == "teacher":
            user = None
        if identifier == None:
            content = utils.the_matrix(user)
            content = {'message': 'success', 'data': content}
            return JsonResponse(content)
        else:
            content = utils.get_project_tree(
                Project.objects.get(identifier=identifier), user)
            content = {'message': 'success', 'data': content}
            return JsonResponse(content)

    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        utils.create_project(body['projectName'],
                             body['productName'], int(body['steps']))

        content = {'message': 'Proyecto creado', 'error': False}
        return JsonResponse(content)

    def put(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        node_id = body['node_id']
        product_name = body['product_name']
        steps = int(body['steps'])
        project = Project.objects.get(identifier=body['project_id'])
        utils.add_nodes_project(steps, product_name, project, node_id)
        content = {'data': 'Editado el flujo del proyecto a las ' +
                   str(datetime.datetime.now()), 'error': False}
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

    def put(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)['data']
        product = Product.objects.get(identifier=body['identifier'])
        product.name = body['name']
        product.start_date = body['startDate']
        product.end_date = body['endDate']
        product.description = body['description']
        product.save()
        content = {'message': 'Producto actualizado at' + datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S'),
            'error': False}
        return JsonResponse(content)


@method_decorator(csrf_exempt, name='dispatch')
class ProjectGraph(View):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        content = utils.get_graph(1)
        return JsonResponse(content)


@method_decorator(csrf_exempt, name='dispatch')
class Resume(View):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        identifier = request.GET.get('identifier')
        resume = utils.resume_groups_project(identifier)
        content = {'message': 'Resume',
                   'error': False, 'data': resume}
        return JsonResponse(content)


@method_decorator(csrf_exempt, name='dispatch')
class Deliveries(View):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        type_ = request.GET.get('type_')
        identifier = request.GET.get('identifier')
        project_id = request.GET.get('project_id')
        project = Project.objects.get(identifier=project_id)
        groups_results = []
        if type_ == 'step':
            context = ProductStep.objects.get(identifier=identifier)
            groups_results = utils.get_groups_delivery_assigment(
                project, context, type_)
        elif type_ == 'product':
            context = Product.objects.get(identifier=identifier)
            groups_results = utils.get_groups_delivery_assigment(
                project, context, type_)
        content = {'message': 'Group Result',
                   'error': False, 'data': groups_results}
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

    def put(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)['data']
        step = ProductStep.objects.get(identifier=body['identifier'])
        step.name = body['name']
        step.start_date = body['startDate']
        step.end_date = body['endDate']
        step.description = body['description']
        step.save()
        content = {'message': 'Etapa actualizada at' + datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S'),
            'error': False}
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
        content = {'message': 'Archivo agregado a las ' + datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S'), 'error': False}
        return JsonResponse(content)


@api_view(['GET', 'PUT'])
def AssignmentDeliveryView(request):
    if request.method == 'GET':
        if request.GET.get('check') == "1":
            type_ = request.GET.get('type_')
            identifier = request.GET.get('identifier')
            user = Session().get_user(
                request.headers['Authorization'].split(' ')[1])
            if user is None:
                return HttpResponse('Unauthorized', status=401)
            delivery = None
            feedback = None
            if type_ == 'step':
                context = ProductStep.objects.get(identifier=identifier)
                group = utils.get_group_by_user_project(context.project, user)
                feedback = Feedback.objects.filter(
                    group=group, product_step=context).first()
                delivery = utils.get_assigment_delivery_by_project_group(
                    context, user, type_, identifier)

            elif type_ == 'product':
                context = Product.objects.get(identifier=identifier)
                group = utils.get_group_by_user_project(context.project, user)
                feedback = Feedback.objects.filter(
                    group=group, product=context).first()
                delivery = utils.get_assigment_delivery_by_project_group(
                    context, user, type_, identifier)
            content = {'message': delivery != None, 'error': False}
            if delivery != None:
                if feedback is not None:
                    feedback = feedback.feedback
                content = {'message': delivery != None, 'error': False,
                           "identifier": delivery.identifier, 'date':  delivery.delivery_date, 'feedback': feedback}
            return JsonResponse(content)

        else:
            import os
            file_name = request.GET.get('identifier')
            delivery = AssignmentDelivery.objects.get(
                identifier=file_name).file_attach
            # file_ = open(os.path.join(os.getcwd(), delivery.file_attach), 'rb')
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
            project = ProductStep.objects.get(
                identifier=identifier).project
            group = utils.get_group_by_user_project(project, user)
            print(group)
            exist = AssignmentDelivery.objects.filter(product_step=ProductStep.objects.get(
                identifier=identifier), user=user).first()
            if exist == None:
                new_file = AssignmentDelivery(file_attach=file_, product_step=ProductStep.objects.get(
                    identifier=identifier), file_name=file_name, user=user, group=group)
                new_file.save()
            else:
                exist.file_attach = file_
                exist.delivery_date = datetime.datetime.now()
                exist.save()
        elif type_ == 'product':
            project = Product.objects.get(
                identifier=identifier).project
            group = utils.get_group_by_user_project(project, user)
            exist = AssignmentDelivery.objects.filter(product=Product.objects.get(
                identifier=identifier), user=user).first()
            if exist == None:
                new_file = AssignmentDelivery(file_attach=file_, product=Product.objects.get(
                    identifier=identifier), file_name=file_name, user=user, group=group)
                new_file.save()
            else:
                exist.file_attach = file_
                exist.delivery_date = datetime.datetime.now()
                exist.save()
        content = {'message': 'Etapa creada', 'error': False}
        return JsonResponse(content)


@method_decorator(csrf_exempt, name='dispatch')
class FeedbackView(View):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        context_type = request.GET.get('type')
        group_id = request.GET.get('group_id')

        product = Product.objects.get(identifier=request.GET.get('identifier'))
        content = product.get_view()
        print(content)
        return JsonResponse(content)

    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        print(body)
        if body['type'] == 'step':
            step = ProductStep.objects.get(identifier=body['identifier'])
            feedback = Feedback(group=Group.objects.get(
                identifier=body['group_id']), feedback=body['text'], product_step=step)
            feedback.save()
        elif body['type'] == 'product':
            product = Product.objects.get(identifier=body['identifier'])
            feedback = Feedback(group=Group.objects.get(
                identifier=body['group_id']), feedback=body['text'], product=product)
            feedback.save()
        content = {'message': 'Feedback creado',
                   'error': False}
        return JsonResponse(content)
        return
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
