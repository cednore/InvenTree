# Generated by Django 3.2.12 on 2022-03-27 01:11

import InvenTree.fields
import django.core.validators
from django.core import serializers
from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields
import djmoney.models.validators


def _convert_model(apps, line_item_ref, extra_line_ref, price_ref):
    """Convert the OrderLineItem instances if applicable to new ExtraLine instances"""
    OrderLineItem = apps.get_model('order', line_item_ref)
    OrderExtraLine = apps.get_model('order', extra_line_ref)

    items_to_change = OrderLineItem.objects.filter(part=None)

    print(f'\nFound {items_to_change.count()} old {line_item_ref} instance(s)')
    print(f'Starting to convert - currently at {OrderExtraLine.objects.all().count()} {extra_line_ref} / {OrderLineItem.objects.all().count()} {line_item_ref} instance(s)')
    for lineItem in items_to_change:
        newitem = OrderExtraLine(
            order=lineItem.order,
            notes=lineItem.notes,
            price=getattr(lineItem, price_ref),
            quantity=lineItem.quantity,
            reference=lineItem.reference,
        )
        newitem.context = {'migration': serializers.serialize('json', [lineItem, ])}
        newitem.save()

        lineItem.delete()
    print(f'Done converting line items - now at {OrderExtraLine.objects.all().count()} {extra_line_ref} / {OrderLineItem.objects.all().count()} {line_item_ref} instance(s)')


def _reconvert_model(apps, line_item_ref, extra_line_ref):
    """Convert ExtraLine instances back to OrderLineItem instances"""
    OrderLineItem = apps.get_model('order', line_item_ref)
    OrderExtraLine = apps.get_model('order', extra_line_ref)

    print(f'\nStarting to convert - currently at {OrderExtraLine.objects.all().count()} {extra_line_ref} / {OrderLineItem.objects.all().count()} {line_item_ref} instance(s)')
    for extra_line in OrderExtraLine.objects.all():
        # regenreate item
        if extra_line.context:
            context_string = getattr(extra_line.context, 'migration')
            if not context_string:
                continue
            [item.save() for item in serializers.deserialize('json', context_string)]
        extra_line.delete()
    print(f'Done converting line items - now at {OrderExtraLine.objects.all().count()} {extra_line_ref} / {OrderLineItem.objects.all().count()} {line_item_ref} instance(s)')


def convert_line_items(apps, schema_editor):
    """convert line items"""
    _convert_model(apps, 'PurchaseOrderLineItem', 'PurchaseOrderExtraLine', 'purchase_price')
    _convert_model(apps, 'SalesOrderLineItem', 'SalesOrderExtraLine', 'sale_price')


def nunconvert_line_items(apps, schema_editor):
    """reconvert line items"""
    _reconvert_model(apps, 'PurchaseOrderLineItem', 'PurchaseOrderExtraLine')
    _reconvert_model(apps, 'SalesOrderLineItem', 'SalesOrderExtraLine')


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0063_alter_purchaseorderlineitem_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesOrderExtraLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', InvenTree.fields.RoundingDecimalField(decimal_places=5, default=1, help_text='Item quantity', max_digits=15, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Quantity')),
                ('reference', models.CharField(blank=True, help_text='Line item reference', max_length=100, verbose_name='Reference')),
                ('notes', models.CharField(blank=True, help_text='Line item notes', max_length=500, verbose_name='Notes')),
                ('target_date', models.DateField(blank=True, help_text='Target shipping date for this line item', null=True, verbose_name='Target Date')),
                ('context', models.JSONField(blank=True, help_text='Additional context for this line', null=True, verbose_name='Context')),
                ('price_currency', djmoney.models.fields.CurrencyField(choices=[], default='', editable=False, max_length=3)),
                ('price', InvenTree.fields.InvenTreeModelMoneyField(blank=True, currency_choices=[], decimal_places=4, default_currency='', help_text='Unit price', max_digits=19, null=True, validators=[djmoney.models.validators.MinMoneyValidator(0)], verbose_name='Price')),
                ('order', models.ForeignKey(help_text='Sales Order', on_delete=django.db.models.deletion.CASCADE, related_name='extra_lines', to='order.salesorder', verbose_name='Order')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PurchaseOrderExtraLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', InvenTree.fields.RoundingDecimalField(decimal_places=5, default=1, help_text='Item quantity', max_digits=15, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Quantity')),
                ('reference', models.CharField(blank=True, help_text='Line item reference', max_length=100, verbose_name='Reference')),
                ('notes', models.CharField(blank=True, help_text='Line item notes', max_length=500, verbose_name='Notes')),
                ('target_date', models.DateField(blank=True, help_text='Target shipping date for this line item', null=True, verbose_name='Target Date')),
                ('context', models.JSONField(blank=True, help_text='Additional context for this line', null=True, verbose_name='Context')),
                ('price_currency', djmoney.models.fields.CurrencyField(choices=[], default='', editable=False, max_length=3)),
                ('price', InvenTree.fields.InvenTreeModelMoneyField(blank=True, currency_choices=[], decimal_places=4, default_currency='', help_text='Unit price', max_digits=19, null=True, validators=[djmoney.models.validators.MinMoneyValidator(0)], verbose_name='Price')),
                ('order', models.ForeignKey(help_text='Purchase Order', on_delete=django.db.models.deletion.CASCADE, related_name='extra_lines', to='order.purchaseorder', verbose_name='Order')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RunPython(convert_line_items, reverse_code=nunconvert_line_items),
    ]
