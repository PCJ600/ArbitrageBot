from rest_framework import serializers

import json
import re
import traceback
import logging
logger = logging.getLogger('app')


def validate_fund_id(fund_id_str):
    if not isinstance(fund_id_str, str):
        return False
    pattern = r'^\d{6}$'
    return bool(re.match(pattern, fund_id_str))


class PercentageField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, str) or not data.endswith('%'):
            raise serializers.ValidationError("format error, should be XX%")
        try:
            # e.g.: convert 0.5% to 0.005
            percentage = float(data[:-1]) / 100
            return percentage
        except ValueError:
            raise serializers.ValidationError("format error, should be XX%")

    def to_representation(self, value):
        return f"{value * 100:.2f}%"


class FundDataSerializer(serializers.Serializer):
    fund_id = serializers.CharField(max_length=6)
    fund_nm = serializers.CharField(max_length=50)
    price = serializers.DecimalField(max_digits=10, decimal_places=4)
    increase_rt = PercentageField()
    fund_nav = serializers.DecimalField(max_digits=10, decimal_places=4)
    nav_dt = serializers.DateField(format="%Y-%m-%d")
    estimate_value = serializers.DecimalField(max_digits=10, decimal_places=4)
    discount_rt = PercentageField()
    apply_status = serializers.CharField(max_length=50)
    redeem_status = serializers.CharField(max_length=50)

    def validate_fund_id(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("fund_id should be 6-digits")
        return value


def parse_one_fund(row):
    result = {}
    try:
        data = row.get('cell')
        serializer = FundDataSerializer(data=data)
        if not serializer.is_valid():
            logger.warn('parse fund error: %r', serializer.errors)
            return None
        result = serializer.validated_data
        logger.debug('parse fund OK: %r', result)
        return result
    except Exception as e:
        logger.error('parse fund exception: %r, traceback: %r', e, traceback.format_exc())
        return None


def parse_fund_data(qdii_data):
    try:
        row_datas = qdii_data.get('rows')
        funds_dict = {}
        for row in row_datas:
            fund_data = parse_one_fund(row)
            if not fund_data or 'fund_id' not in fund_data:
                logger.debug('parse fund failed, skip data %r', row)
                continue
            fund_id = fund_data.get('fund_id')
            funds_dict[fund_id] = fund_data

        return funds_dict
    except Exception as e:
        logger.error('notify exception: %r, traceback: %r', e, traceback.format_exc())
        return None
