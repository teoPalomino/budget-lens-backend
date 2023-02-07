import os

def create_update_receipt(sender, instance):
    try:
        old_receipt_image = instance.__class__.objects.get(id=instance.id).receipt_image
        try:
            new_updated_receipt_image = instance.receipt_image
        except ValueError:
            new_updated_receipt_image = None
        if new_updated_receipt_image != old_receipt_image: 
            if os.path.exists(old_receipt_image.path):
                os.remove(old_receipt_image.path)
        return True
    except instance.DoesNotExist:
        return True
    except Exception as e:
        print(str(e))
        return False
