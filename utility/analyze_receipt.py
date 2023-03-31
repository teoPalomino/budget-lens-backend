import os
from django.db import models
from merchant.models import Merchant
from item.models import Item
def analyze_receipts(file,passed_receipt):
    if os.getenv('APP_ENV') != 'test':
        path_to_sample_documents = file
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import DocumentAnalysisClient

        endpoint = "https://budgetlens.cognitiveservices.azure.com/"
        key = 'eda67d70c1d04f5d964946779e494672'

        document_analysis_client = DocumentAnalysisClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        with open(path_to_sample_documents, "rb") as f:
            poller = document_analysis_client.begin_analyze_document(
                "prebuilt-receipt", document=f, locale="en-US"
            )
        receipts = poller.result()

        receipt_text = ""
        for idx, receipt in enumerate(receipts.documents):
            receipt_text += "--------Analysis of receipt #{}--------".format(idx + 1)
            receipt_text +=  "Receipt type: {}".format(receipt.doc_type or "N/A")
            merchant_name = receipt.fields.get("MerchantName")
            if merchant_name:
                receipt_merchant, created = Merchant.objects.get_or_create(name=merchant_name.value)
                passed_receipt.merchant = receipt_merchant
                passed_receipt.save()
                receipt_text +=  (
                    "Merchant Name: {} has confidence: {}".format(
                        merchant_name.value, merchant_name.confidence
                    )
                )
            transaction_date = receipt.fields.get("TransactionDate")
            if transaction_date:
                receipt_text +=(
                    "Transaction Date: {} has confidence: {}".format(
                        transaction_date.value, transaction_date.confidence
                    )
                )
            if receipt.fields.get("Items"):
                receipt_text +=("Receipt items:")
                for idx, item in enumerate(receipt.fields.get("Items").value):
                    receipt_text +=("...Item #{}".format(idx + 1))
                    item_description = item.value.get("Description")
                    if item_description:
                        receipt_text +=(
                            "......Item Description: {} has confidence: {}".format(
                                item_description.value, item_description.confidence
                            )
                        )
                    item_quantity = item.value.get("Quantity")
                    if item_quantity:
                        receipt_text +=(
                            "......Item Quantity: {} has confidence: {}".format(
                                item_quantity.value, item_quantity.confidence
                            )
                        )
                    item_price = item.value.get("Price")
                    if item_price:
                        receipt_text +=(
                            "......Individual Item Price: {} has confidence: {}".format(
                                item_price.value, item_price.confidence
                            )
                        )


                    item_total_price = item.value.get("TotalPrice")
                    if item_total_price:
                        receipt_text +=(
                            "......Total Item Price: {} has confidence: {}".format(
                                item_total_price.value, item_total_price.confidence
                            )
                        )
                        if item_price is not None:
                            Item.objects.create(
                                user=passed_receipt.user,
                                receipt=passed_receipt,
                                name=item_description.value,
                                price=item_price.value,
                            )
                        else:
                            Item.objects.create(
                                user=passed_receipt.user,
                                receipt=passed_receipt,
                                name=item_description.value,
                                price=item_total_price.value,
                            )
            subtotal = receipt.fields.get("Subtotal")
            if subtotal:
                receipt_text +=(
                    "Subtotal: {} has confidence: {}".format(
                        subtotal.value, subtotal.confidence
                    )
                )
            tax = receipt.fields.get("TotalTax")
            if tax:
                passed_receipt.tax = tax.value

                receipt_text +=("Total tax: {} has confidence: {}".format(tax.value, tax.confidence))
            tip = receipt.fields.get("Tip")
            if tip:
                passed_receipt.tip = tip.value
                receipt_text +=("Tip: {} has confidence: {}".format(tip.value, tip.confidence))
            total = receipt.fields.get("Total")
            if total:
                passed_receipt.total = total.value
                receipt_text +=("Total: {} has confidence: {}".format(total.value, total.confidence))
            receipt_text += ("--------------------------------------")
            passed_receipt.save()
        return receipt_text

if __name__ == "__main__":
    analyze_receipts()