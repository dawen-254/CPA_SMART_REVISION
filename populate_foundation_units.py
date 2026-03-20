import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.content.models import Level, Part, Unit

def populate_units():
    # 1. Create Foundation Level
    foundation_level, created = Level.objects.get_or_create(
        name="foundation",
        defaults={
            "code": "F",
            "description": "Foundation level of CPA examination",
            "order": 1
        }
    )
    if created:
        print(f"Created Level: {foundation_level}")
    else:
        print(f"Level already exists: {foundation_level}")

    # 2. Create Parts A and B
    part_a, created = Part.objects.get_or_create(
        level=foundation_level,
        name="part_a",
        defaults={"description": "First part of Foundation level", "order": 1}
    )
    if created:
        print(f"Created Part: {part_a}")

    part_b, created = Part.objects.get_or_create(
        level=foundation_level,
        name="part_b",
        defaults={"description": "Second part of Foundation level", "order": 2}
    )
    if created:
        print(f"Created Part: {part_b}")

    # 3. Create Units for Part A
    part_a_units = [
        ("FA", "Financial Accounting", "Introduction to financial accounting principles"),
        ("CS", "Communication Skills", "Effective communication in a business context"),
        ("BL", "Business Law", "Legal environment and commercial law"),
    ]

    for code, name, desc in part_a_units:
        unit, created = Unit.objects.get_or_create(
            code=code,
            defaults={
                "name": name,
                "level": foundation_level,
                "part": part_a,
                "description": desc,
                "order": 1
            }
        )
        if created:
            print(f"Created Unit: {unit}")
        else:
            # Update part if it was already created but maybe assigned incorrectly
            unit.part = part_a
            unit.save()

    # 4. Create Units for Part B
    part_b_units = [
        ("QA", "Quantitative Analysis", "Mathematical and statistical techniques"),
        ("EC", "Economics", "Principles of micro and macroeconomics"),
        ("IT", "Information Technology", "Business information systems"),
    ]

    for code, name, desc in part_b_units:
        unit, created = Unit.objects.get_or_create(
            code=code,
            defaults={
                "name": name,
                "level": foundation_level,
                "part": part_b,
                "description": desc,
                "order": 1
            }
        )
        if created:
            print(f"Created Unit: {unit}")
        else:
            unit.part = part_b
            unit.save()

if __name__ == "__main__":
    populate_units()
    print("Population complete!")
