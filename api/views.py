
from django.http import FileResponse
from django.views import View
from django.http import JsonResponse
from api.models import Project as Project
from api.models import Product as Product
from api.models import Node as Node
from api.models import ProductStep as ProductStep
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
        return JsonResponse(content)
    
    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        node = None
        if 'referenceType' not in  body:
            pass
        elif body['referenceType'] == "step":
            step = ProductStep.objects.get(identifier=body['reference_id'])
            node = Node.objects.get(product_step=step)
        elif body['referenceType'] == "product":
            product_preview = Product.objects.get(identifier=body['reference_id'])
            node = Node.objects.get(product=product_preview)
        product = Node()
        product = product.create(body, "product", node)
        content = {'message': 'Producto creado', 'error': False, 'node': product.identifier}
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
        content = {'data': step , 'error': False}
        return JsonResponse(content)
        
    
    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        node = None
        if 'referenceType' not in  body:
            pass
        elif body['referenceType'] == "step":
            step = ProductStep.objects.get(identifier=body['reference_id'])
            node = Node.objects.get(product_step=step)
        elif body['referenceType'] == "product":
            product_preview = Product.objects.get(identifier=body['reference_id'])
            node = Node.objects.get(product=product_preview)
        product = Node()
        product = product.create(body, "step", node)
        content = {'message': 'Etapa creada', 'error': False, 'node': product.identifier}
        return JsonResponse(content)
 
@method_decorator(csrf_exempt, name='dispatch')
class FilesView(View):
    permission_classes = ()
    authentication_classes = ()
    def get(self, request):
        import os
        file_name = request.GET.get('file_name')
        file_ = open(os.path.join(os.getcwd(), file_name), 'rb')
        response = FileResponse(file_)
        return response

    def put(self, request):
        file_ = request.data.get('file')
        type_ = request.data.get('type_')
        file_name = request.data.get('file_name')
        identifier = request.data.get('identifier')
        if type_ == 'project':
            new_file = Files(file_attach=file_, project=Project.objects.get(identifier=identifier), file_name=file_name)
            new_file.save()
        elif type_ == 'step':
            new_file = Files(file_attach=file_, product_step=ProductStep.objects.get(identifier=identifier), file_name=file_name)
            new_file.save()
        elif type_ == 'product':
            new_file = Files(file_attach=file_, product=Product.objects.get(identifier=identifier), file_name=file_name)
            new_file.save()
        content = {'message': 'Etapa creada', 'error': False}
        return JsonResponse(content)