from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    """User registration schema"""
    email = fields.Email(required=True)
    firstName = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    lastName = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    password = fields.Str(required=True, validate=validate.Length(min=6))
    role = fields.Str(required=True, validate=validate.OneOf(['retailer', 'distributor', 'manufacturer']))
    businessName = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True)
    phoneNumber = fields.Str(allow_none=True)
    whatsappNumber = fields.Str(allow_none=True)

class ProductSchema(Schema):
    """Product creation schema"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)
    sku = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    categoryId = fields.UUID(allow_none=True)
    imageUrl = fields.Str(allow_none=True)
    basePrice = fields.Decimal(allow_none=True, places=2)

class OrderSchema(Schema):
    """Order creation schema"""
    distributorId = fields.UUID(required=True)
    items = fields.List(fields.Dict(), required=True, validate=validate.Length(min=1))
    notes = fields.Str(allow_none=True)
    deliveryMode = fields.Str(validate=validate.OneOf(['pickup', 'delivery']), missing='delivery')

class PartnershipSchema(Schema):
    """Partnership request schema"""
    partnerId = fields.UUID(required=True)
    partnershipType = fields.Str(required=True, validate=validate.OneOf(['supplier', 'distributor', 'retailer']))

class FavoriteSchema(Schema):
    """Favorite creation schema"""
    favoriteUserId = fields.UUID(required=True)
    favoriteType = fields.Str(required=True, validate=validate.OneOf(['manufacturer', 'distributor', 'retailer']))

class SearchHistorySchema(Schema):
    """Search history schema"""
    searchTerm = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    searchType = fields.Str(required=True, validate=validate.OneOf(['product', 'manufacturer', 'distributor']))
    resultCount = fields.Int(required=True, validate=validate.Range(min=0)) 