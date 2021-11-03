
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


def add_nodes_project(steps, product_name, project, node_id):
    from api.models import Product
    from api.models import ProductStep
    from api.models import Node
    product = Product(name=product_name, project=project)
    product.save()
    last = Node.objects.get(identifier=node_id)
    for i in range(steps):
        step = ProductStep(product=product, project=project)
        step.save()
        node = Node(product_step=step, initial=False,
                    preview=last, project=project)
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
    from api.models import UserProfile
    from api.models import AssignmentDelivery
    from api.models import ProductStep
    from api.models import Product
    groups = UserGroup.objects.filter(user=user)
    for group in groups:
        if group.group.project != context.project:
            continue
        user_groups = UserGroup.objects.filter(group=group.group)
        delivery = None
        for user_group in user_groups:
            if context_type == "product":
                delivery = AssignmentDelivery.objects.filter(
                    product=context, user=user_group.user).first()
                if delivery is not None:
                    break
            elif context_type == "step":
                delivery = AssignmentDelivery.objects.filter(
                    product_step=context, user=user_group.user).first()
                if delivery is not None:
                    break
        return delivery


def get_group_users(group):
    from api.models import UserGroup
    from api.models import UserProfile
    user_groups = UserGroup.objects.filter(group=group)
    users = []
    for user_group in user_groups:
        users.append(UserProfile.objects.filter(
            user=user_group.user).first().get_user_data())
    return {'name': group.name, 'identifier': group.identifier, 'users': users}


def get_groups_delivery_assigment(project, context, context_type):
    from api.models import Group
    from api.models import UserGroup
    from api.models import UserProfile
    from api.models import AssignmentDelivery
    from api.models import ProductStep
    from api.models import Product
    groups = Group.objects.filter(project=project)
    return_groups = []
    for group in groups:
        user_groups = UserGroup.objects.filter(group=group)
        delivery = None
        for user_group in user_groups:
            if context_type == "product":
                delivery = AssignmentDelivery.objects.filter(
                    product=context, user=user_group.user).first()
                if delivery is not None:
                    break
            elif context_type == "step":
                delivery = AssignmentDelivery.objects.filter(
                    product_step=context, user=user_group.user).first()
                if delivery is not None:
                    break
        group_data = get_group_users(group)
        group_data['delivery'] = delivery
        if delivery is not None:
            group_data['delivery'] = delivery.assigment_data()
        return_groups.append(group_data)
    return return_groups


def get_groups_delivery_assigment_fast(project, context, context_type):
    from api.models import Group
    from api.models import UserGroup
    from api.models import UserProfile
    from api.models import AssignmentDelivery
    from api.models import ProductStep
    from api.models import Product
    groups = Group.objects.filter(project=project)
    return_groups = []
    for group in groups:
        delivery = None
        if context_type == "product":
            delivery = AssignmentDelivery.objects.filter(
                product=context, group=group).first()
        elif context_type == "step":
            delivery = AssignmentDelivery.objects.filter(
                product_step=context, group=group).first()
        group_data = {'name': group.name,
                      'identifier': group.identifier, 'delivery': delivery}
        if delivery is not None:
            group_data['delivery'] = delivery.assigment_data()
        return_groups.append(group_data)
    return return_groups


def resume_node_search(node, data, project):
    from api.models import ProductStep
    from api.models import Product
    from api.models import Node
    if node.product_step is not None:
        d = {'name': node.product_step.name, 'type': 'step', 'data': get_groups_delivery_assigment_fast(
            project, node.product_step, 'step'), 'id': node.identifier}
        data.append(d)
    elif node.product is not None:
        d = {'name': node.product.name, 'type': 'product', 'data': get_groups_delivery_assigment_fast(
            project, node.product, 'product'), 'id': node.identifier}
        data.append(d)
    next_nodes = Node.objects.filter(project=project, preview=node)
    for next_node in next_nodes:
        resume_node_search(next_node, data, project)


def resume_groups_project(identifier):
    from api.models import Project
    from api.models import Group
    from api.models import ProductStep
    from api.models import Product
    from api.models import Node
    project = Project.objects.filter(identifier=identifier).first()
    groups = Group.objects.filter(project=project)
    first_node = Node.objects.filter(project=project, preview=None).first()
    data = []
    resume_node_search(first_node, data, project)
    return data


def get_group_by_user_project(project, user):
    from api.models import Group
    from api.models import UserGroup
    for user_group in UserGroup.objects.filter(user=user):
        if user_group.group.project == project:
            return user_group.group


def get_node_dict(node, user=None):
    from api.models import Project
    from api.models import Product
    from api.models import ProductStep
    if node.product is not None:
        product = node.product
        d = {'project_id': product.project.identifier, 'node_id': node.identifier, 'id': product.identifier, 'name': product.name,
             'children': [], 'type': 'product', 'start_date': format_date(product.start_date), 'end_date': format_date(product.end_date)}
        if user is not None:
            delivery = get_assigment_delivery_by_project_group(
                product, user, 'product', product.project.identifier)
            d['delivery'] = delivery != None
        return d
    elif node.product_step is not None:
        product = node.product_step
        d = {'project_id': product.project.identifier, 'node_id': node.identifier, 'id': product.identifier, 'name': product.name,
             'children': [], 'type': 'step', 'start_date': format_date(product.start_date), 'end_date': format_date(product.end_date)}
        if user is not None:
            delivery = get_assigment_delivery_by_project_group(
                product, user, 'step', product.project.identifier)
            d['delivery'] = delivery != None
        return d
    else:
        return {'node_id': node.identifier, 'name': 'inicio'}


def node_search(first, user=None, prev_complish=False):
    from api.models import Project
    from api.models import Product
    from api.models import ProductStep
    from api.models import Node
    next_nodes = Node.objects.filter(preview=first)
    tree = get_node_dict(first, user)
    tree_past_del = False
    if 'delivery' in tree:
        tree_past_del = tree['delivery']
    for next_node in next_nodes:
        if next_node is None:
            continue
        childs = node_search(next_node, user, tree_past_del)
        tree['children'].append(childs)
    tree['delivery_past'] = prev_complish
    return tree


def get_project_tree(project_id):
    from api.models import Project
    from api.models import Node
    project = Project.objects.get(identifier=project_id)
    first_node = Node.objects.filter(project=project, preview=None).first()
    tree = node_search(first_node)
    return tree


def get_project_tree(project, user=None):
    from api.models import Node
    first_node = Node.objects.filter(project=project, preview=None).first()
    if first_node is None:
        return {'project': project.serialize(), 'tree': {}}
    tree = node_search(first_node, user, True)
    return {'project': project.serialize(), 'tree': tree}


def the_matrix(user=None):
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
        tree = node_search(first_node, user, True)
        return_projects_format.append(
            {'project': project.serialize(), 'tree': tree})
    return return_projects_format
