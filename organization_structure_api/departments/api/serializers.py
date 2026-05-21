from rest_framework import serializers

from departments.models import Department
from employees.api.serializers import EmployeeShortSerializer

def get_department_root(department: Department) -> Department:
    current = department

    while current.parent is not None:
        current = current.parent

    return current

def get_department_tree_ids(department: Department) -> list[int]:
    ids = [department.id]

    for child in department.children.all():
        ids.extend(get_department_tree_ids(child))

    return ids

class DepartmentShortSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Department
        fields = ("id", "name", "parent_id", "created_at")
        read_only_fields = fields

class DepartmentCreateSerializer(serializers.ModelSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source="parent",
        required=False,
        allow_null=True,
        default=None,
    )
    
    class Meta:
        model = Department
        fields = ("name", "parent_id")
    
    def validate_name(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("name cannot be empty.")
        return value

    def validate(self, attrs):
        name = attrs.get("name")
        parent = attrs.get("parent")

        if parent is None:
            if Department.objects.filter(name=name, parent__isnull=True).exists():
                raise serializers.ValidationError(
                    {"name": "Root department with this name already exists."}
                )

            return attrs

        root = get_department_root(parent)
        tree_ids = get_department_tree_ids(root)

        if Department.objects.filter(id__in=tree_ids, name=name).exists():
            raise serializers.ValidationError(
                {"name": "Department with this name already exists in this tree."}
            )

        return attrs
    
class DepartmentUpdateSerializer(serializers.ModelSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source="parent",
        required=False,
        allow_null=True,
    )
    
    class Meta:
        model = Department
        fields = ("name", "parent_id")
        
    def validate_name(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("name cannot be empty.")
        return value

    def validate(self, attrs):
        name = attrs.get("name", self.instance.name)
        parent = attrs.get("parent", self.instance.parent)
    
        moving_subtree_ids = get_department_tree_ids(self.instance)
    
        if Department.objects.filter(
            id__in=moving_subtree_ids,
            name=name,
        ).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError(
                {"name": "Department with this name already exists in this subtree."}
            )
    
        if parent is None:
            if Department.objects.filter(
                name=name,
                parent__isnull=True,
            ).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError(
                    {"name": "Root department with this name already exists."}
                )
    
            return attrs
    
        target_root = get_department_root(parent)
        target_tree_ids = get_department_tree_ids(target_root)
    
        moving_subtree_names = list(
            Department.objects.filter(id__in=moving_subtree_ids)
            .exclude(pk=self.instance.pk)
            .values_list("name", flat=True)
        )
        moving_subtree_names.append(name)
    
        conflict_exists = (
            Department.objects.filter(
                id__in=target_tree_ids,
                name__in=moving_subtree_names,
            )
            .exclude(id__in=moving_subtree_ids)
            .exists()
        )
    
        if conflict_exists:
            raise serializers.ValidationError(
                {"name": "Department name conflict in target tree."}
            )
    
        return attrs
    
class DepartmentTreeNodeSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(read_only=True)
    employees = EmployeeShortSerializer(many=True, read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ("id", "name", "parent_id", "created_at", "employees", "children")
        read_only_fields = fields

    def get_children(self, obj):
        depth = self.context.get("depth", 1)
        if depth <= 0:
            return []

        children = obj.children.all().order_by("created_at")
        serializer = DepartmentTreeNodeSerializer(
            children,
            many=True,
            context={**self.context, "depth": depth - 1},
        )
        return serializer.data

class DepartmentDetailSerializer(serializers.Serializer):
    department = DepartmentShortSerializer(source="*")
    employees = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    def get_employees(self, obj):
        if not self.context.get("include_employees", True):
            return []

        employees = obj.employees.all().order_by("created_at", "full_name")
        return EmployeeShortSerializer(employees, many=True).data

    def get_children(self, obj):
        depth = self.context.get("depth", 1)
        if depth <= 0:
            return []

        children = obj.children.all().order_by("created_at")
        serializer = DepartmentTreeNodeSerializer(
            children,
            many=True,
            context={**self.context, "depth": depth - 1},
        )
        return serializer.data