from django.db import models

# Create your models here.
from django.db import models
from django.contrib.postgres.fields import JSONField

from api.utils import format_date

# Create your models here.
class Project(models.Model):
    identifier = models.AutoField(blank=False, primary_key=True)
    name = models.CharField(max_length=80, blank=False, default='')
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    def create(self, data):
        name = data['name']
        start_date = data['start_date']
        end_date = data['end_date']
        description = data['description']
        project = Project(name=name, start_date=start_date, end_date=end_date, description=description)
        project.save()
        return True
    def serialize(self):
        files = Files.objects.filter(project=self)
        return {'id': self.identifier, 'description': self.description, 'name': self.name, 'end_date': format_date(self.end_date), 'start_date': format_date(self.start_date), 'files': list(map(lambda x : {'file': x.file_attach.url, 'file_name': x.file_name}, files))}


class Product(models.Model):
    identifier = models.AutoField(blank=False, primary_key=True)
    name = models.CharField(max_length=80, blank=False, default='')
    start_date = models.DateTimeField()
    description = models.TextField()
    end_date = models.DateTimeField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    requirement = models.IntegerField(null=True)
    def create(self, data):
        name = data['name']
        start_date = data['start_date']
        end_date = data['end_date']
        description = data['description']
        project = Project(identifier=data['project_id'])
        requirement = None
        if 'requirement' in data:
            requirement = data['requirement']
        product = Product(name=name, start_date=start_date, end_date=end_date, project=project, requirement=requirement, description=description)
        product.save()
        return product
    def get_view(self):
        files = Files.objects.filter(project=self.project)
        project = {'id': self.project.identifier, 'name': self.project.name, 'end_date': format_date(self.project.end_date), 'start_date': format_date(self.project.start_date), 'files': list(map(lambda x : {'file': x.file_attach.url, 'file_name': x.file_name}, files))}
        files = Files.objects.filter(product=self)
        product = {'name': self.name, 'end_date': format_date(self.end_date), 'description': self.description,  'start_date': format_date(self.start_date), 'files': map(lambda x : {'file': x.file_attach.url}, files)}
        return  {'project': project, 'product': product}


class ProductStep(models.Model):
    identifier = models.AutoField(blank=False, primary_key=True)
    name = models.CharField(max_length=80, blank=False, default='')
    start_date = models.DateTimeField()
    description = models.TextField()
    end_date = models.DateTimeField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    
    def create(self, data):
        name = data['name']
        start_date = data['start_date']
        end_date = data['end_date']
        description = data['description']
        product = None
        project = None
        if 'product_id' in data:
            product = Product.objects.filter(identifier=data['product_id']).first()
        if 'project_id' in data:
            project = Project.objects.filter(identifier=data['project_id']).first()        
        step = ProductStep(name=name, start_date=start_date, end_date=end_date, product=product, project=project, description=description)
        step.save()
        return step
    def serialize(self):
        files = Files.objects.filter(product_step=self)
        return {'id': self.identifier, 'name': self.name, 'end_date': format_date(self.end_date), 'description': self.description, 'start_date': format_date(self.start_date), 'files': list(map(lambda x : {'file': x.file_attach.url, 'file_name': x.file_name}, files))}


class Files(models.Model):
    identifier = models.AutoField(blank=False, primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    product_step = models.ForeignKey(ProductStep, on_delete=models.CASCADE, null=True)
    file_name = models.CharField(max_length=80, blank=False, default='')
    file_attach = models.FileField(upload_to='uploads/')
#    def create(self, data):
#        project = Project(identifier=data['project_id'])
##        name = data['name']
#        product = Product(identifier=data['product_id'])
#        product_step = ProductStep(identifier=data['product_step_id'])
#        file_ = Files(name=name, project=project, product=product, product_step=product_step)
#        file_.save()
#        return True


class Node(models.Model):
    identifier = models.AutoField(blank=False, primary_key=True)
    initial = models.BooleanField(default=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    product_step = models.ForeignKey(ProductStep, on_delete=models.CASCADE, null=True)
    preview = models.ForeignKey('Node',null=True,blank=True,on_delete=models.CASCADE)
    def create(self, data, type_, preview):
        if type_ == "product":
            product = Product().create(data)
            node = Node(product=product, project=Project.objects.get(identifier=data['project_id']), preview=preview)
            node.save()
            return node
        elif type_ == "step":
            product_step = ProductStep().create(data)
            node = Node(product_step=product_step, project=Project.objects.get(identifier=data['project_id']), preview=preview)
            node.save()
            return node