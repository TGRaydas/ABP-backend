
def product_children(product):
    from api.models import ProductStep
    from api.models import Product
    product_step = ProductStep.objects.filter(product=product)
    children = {'id': product.identifier, 'name': product.name, 'children': [
    ], 'type': 'product', 'start_date': product.start_date, 'end_date': product.end_date}
    for step in product_step:
        step_children = {'id': step.identifier, 'name': step.name, 'children': [
        ], 'start_date': step.start_date, 'end_date': step.end_date, 'type': 'step'}
        product_childs = Product.objects.filter(requirement=step.identifier)
        for product_child in product_childs:
            step_children['children'].append({'id': product.identifier, 'name': product_child.name, 'children': product_children(
                product_child), 'type': 'product', 'end_date': product.end_date, 'start_date': product.start_date})
        children['children'].append(step_children)
    return children


def get_graph(project_id):
    from api.models import Project
    from api.models import Product
    from api.models import ProductStep
    project = Project.objects.get(identifier=project_id)
    start_product = Product.objects.filter(project=project, requirement=None)
    tree = {"name": project.name, "children": [],
            "type": 'project', 'id': project.identifier}
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
    if date != None:
        return date.strftime('%Y-%m-%dT%H:%M:%S')
    return None


def get_node_dict(node):
    from api.models import Project
    from api.models import Product
    from api.models import ProductStep
    if node.product is not None:
        product = node.product
        return {'node_id': node.identifier, 'id': product.identifier, 'name': product.name, 'children': [], 'type': 'product', 'start_date': format_date(product.start_date), 'end_date': format_date(product.end_date)}
    elif node.product_step is not None:
        product = node.product_step
        return {'node_id': node.identifier, 'id': product.identifier, 'name': product.name, 'children': [], 'type': 'step', 'start_date': format_date(product.start_date), 'end_date': format_date(product.end_date)}
    else:
        return {'node_id': node.identifier, 'name': 'inicio'}


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


def get_project_tree(project_id):
    from api.models import Project
    from api.models import Node
    project = Project.objects.get(identifier=project_id)
    first_node = Node.objects.filter(project=project, preview=None).first()
    tree = node_search(first_node)
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
            return_projects_format.append(
                {'project': project.serialize(), 'tree': {}})
            continue
        tree = node_search(first_node)
        return_projects_format.append(
            {'project': project.serialize(), 'tree': tree})
    return return_projects_format


def create_project(project_name, product_name, steps):
    from api.models import Project
    from api.models import Product
    from api.models import ProductStep
    from api.models import Node
    project = Project(name=project_name)
    project.save()
    product = Product(name=product_name, project=project)
    product.save()
    last = None
    for i in range(steps):
        step = ProductStep(product=product, project=project)
        step.save()
        node = Node(product_step=step, initial=True if i ==
                    0 else False, preview=None if i == 0 else last, project=project)
        node.save()
        last = node
    node = Node(product=product, initial=False, preview=last, project=project)
    node.save()


def get_groups_by_project(project):
    from api.models import Group
    from api.models import UserGroup
    from api.models import UserProfile
    groups = Group.objects.filter(project=project)
    return_groups = []
    for group in groups:
        user_groups = UserGroup.objects.filter(group=group)
        users = []
        for user_group in user_groups:
            users.append(UserProfile.objects.filter(
                user=user_group.user).first().get_user_data())
        return_groups.append(
            {'name': group.name, 'identifier': group.identifier, 'users': users})
    return return_groups


def get_assigment_delivery_by_project_group(context, user, context_type, identifier):
    from api.models import Group
    from api.models import UserGroup
    from api.models import AssignmentDelivery
    from api.models import ProductStep
    from api.models import Product
    delivery = None
    if context_type == "product":
        project = context.project
        groups = Group.objects.filter(project=project)
        users_groups = UserGroup.objects.filter(user=user)
        for group in groups:
            if users_groups.filter(group=group).count() > 0:
                for user_group in users_groups.filter(group=group):
                    context_user = user_group.user
                    delivery = AssignmentDelivery.objects.filter(
                        product=Product.objects.get(identifier=identifier), user=context_user).first()
                    break
                break
    elif context_type == "step":
        project = context.project
        groups = Group.objects.filter(project=project)
        users_groups = UserGroup.objects.filter(user=user)
        for group in groups:
            if users_groups.filter(group=group).count() > 0:
                for user_group in UserGroup.objects.filter(group=group):
                    print(user_group.user)
                    context_user = user_group.user
                    delivery = AssignmentDelivery.objects.filter(
                        product_step=ProductStep.objects.get(identifier=identifier), user=context_user).first()
                    break
                break
    return delivery
