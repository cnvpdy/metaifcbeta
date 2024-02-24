import ifcopenshell


def calculate_wall_areas(walls):
    total_area = 0
    for wall in walls:
        for relation in wall.IsDefinedBy:
            if relation.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                quantities = relation.RelatingPropertyDefinition.Quantities
                for quantity in quantities:
                    if quantity.Name == "NetSideArea":
                        total_area += quantity.AreaValue
            elif relation.RelatingPropertyDefinition.is_a("IfcPropertySet"):
                for property in relation.RelatingPropertyDefinition.HasProperties:
                    if property.Name == "NetSideArea":
                        # 여기서 property 값을 올바르게 처리
                        # 예: total_area += property.NominalValue.wrappedValue 또는 적절한 속성 접근 방법 사용
                        pass
    return total_area