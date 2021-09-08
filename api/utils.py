def product_children(product):
    from api.models import ProductStep
    from api.models import Product
    product_step = ProductStep.objects.filter(product=product)
    children = {'id': product.identifier ,'name': product.name, 'children':[], 'type':'product', 'start_date': product.start_date, 'end_date':product.end_date}
    for step in product_step:
        step_children = {'id': step.identifier, 'name':step.name, 'children':[], 'start_date': step.start_date, 'end_date':step.end_date, 'type':'step'}
        product_childs = Product.objects.filter(requirement = step.identifier)
        for product_child in product_childs:
            step_children['children'].append({'id': product.identifier, 'name': product_child.name,'children':product_children(product_child), 'type':'product', 'end_date': product.end_date, 'start_date': product.start_date})
        children['children'].append(step_children)
    return children

def get_graph(project_id):
    from api.models import Project
    from api.models import Product
    from api.models import ProductStep
    project = Project.objects.get(identifier=project_id)
    start_product = Product.objects.filter(project=project, requirement=None)
    tree = {"name": project.name, "children": [], "type": 'project', 'id': project.identifier}
    for product in start_product:
        product_step = ProductStep(product=product)
        children = product_children(product)
        tree['children'].append(children)
    return tree

def get_projects():
    from api.models import Project
    projects = Project.objects.all()
    return_projects = []
    for project in projects:
        data = get_graph(project.identifier)
        return_projects.append(data)
    return return_projects
    

def format_date(date):
    return date.strftime('%Y-%m-%dT%H:%M:%S')


def get_node_dict(node):
    from api.models import Project
    from api.models import Product
    from api.models import ProductStep
    if node.product is not None:
        product = node.product
        return  {'node_id':node.identifier, 'id': product.identifier ,'name': product.name, 'children':[], 'type':'product', 'start_date': format_date(product.start_date), 'end_date':format_date(product.end_date)}
    elif node.product_step is not None:
        product = node.product_step
        return  {'node_id':node.identifier, 'id': product.identifier ,'name': product.name, 'children':[], 'type':'step', 'start_date': format_date(product.start_date), 'end_date':format_date(product.end_date)}
    else:
        return  {'node_id': node.identifier ,'name': 'inicio'}



def node_search(first):
    from api.models import Project
    from api.models import Product
    from api.models import ProductStep
    from api.models import Node
    next_nodes = Node.objects.filter(preview=first)
    tree = get_node_dict(first)
    for next_node in next_nodes:
        if next_node is None:
            continue
        childs = node_search(next_node)
        tree['children'].append(childs)
    return tree
            
    

def the_matrix():
    from api.models import Project
    from api.models import Product
    from api.models import ProductStep
    from api.models import Node
    return_projects_format = []
    projects = Project.objects.all()
    for project in projects:
        first_node = Node.objects.filter(project=project, preview=None).first()
        if first_node is None:
            return_projects_format.append({'project': project.serialize(), 'tree': {}})
            continue
        tree = node_search(first_node)
        return_projects_format.append({'project': project.serialize(), 'tree': tree})
    return return_projects_format
        