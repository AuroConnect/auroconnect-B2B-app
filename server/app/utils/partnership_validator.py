from app.models.user import User
from app.models.partnership import Partnership
from app import db

class PartnershipValidator:
    """Utility class to validate partnership rules based on business roles"""
    
    @staticmethod
    def get_allowed_partnership_types(requester_role, partner_role):
        """
        Get allowed partnership types based on requester and partner roles
        
        Rules:
        - Manufacturer: Can only partner with Distributors
        - Distributor: Can partner with Manufacturers and Retailers (not other Distributors)
        - Retailer: Can only partner with Distributors (not other Retailers)
        """
        
        # Define allowed partnerships
        allowed_partnerships = {
            'manufacturer': {
                'distributor': 'MANUFACTURER_DISTRIBUTOR'
            },
            'distributor': {
                'manufacturer': 'DISTRIBUTOR_MANUFACTURER',
                'retailer': 'DISTRIBUTOR_RETAILER'
            },
            'retailer': {
                'distributor': 'RETAILER_DISTRIBUTOR'
            }
        }
        
        # Check if this partnership is allowed
        if requester_role in allowed_partnerships and partner_role in allowed_partnerships[requester_role]:
            return allowed_partnerships[requester_role][partner_role]
        
        return None
    
    @staticmethod
    def validate_partnership_request(requester_id, partner_id):
        """
        Validate if a partnership request is allowed based on business rules
        
        Returns:
        - (is_valid, error_message, partnership_type)
        """
        try:
            # Get user details
            requester = User.query.get(requester_id)
            partner = User.query.get(partner_id)
            
            if not requester or not partner:
                return False, "One or both users not found", None
            
            # Check if users are active
            if not requester.is_active or not partner.is_active:
                return False, "One or both users are inactive", None
            
            # Check if trying to partner with self
            if requester_id == partner_id:
                return False, "Cannot create partnership with yourself", None
            
            # Get allowed partnership type
            partnership_type = PartnershipValidator.get_allowed_partnership_types(
                requester.role, partner.role
            )
            
            if not partnership_type:
                return False, f"{requester.role.title()}s cannot partner with {partner.role.title()}s", None
            
            # Check if partnership already exists
            existing_partnership = Partnership.query.filter(
                ((Partnership.requester_id == requester_id) & (Partnership.partner_id == partner_id)) |
                ((Partnership.requester_id == partner_id) & (Partnership.partner_id == requester_id))
            ).first()
            
            if existing_partnership:
                if existing_partnership.status == 'active':
                    return False, "Partnership already exists", None
                elif existing_partnership.status == 'pending':
                    return False, "Partnership request already pending", None
            
            return True, None, partnership_type
            
        except Exception as e:
            return False, f"Validation error: {str(e)}", None
    
    @staticmethod
    def get_available_partners_for_role(user_role, user_id):
        """
        Get available partners for a specific user role
        
        Returns list of users that can be partnered with based on role restrictions
        """
        try:
            # Get all active users except the current user
            all_users = User.query.filter(
                User.id != user_id,
                User.is_active == True
            ).all()
            
            # Get current user's existing partnerships
            existing_partnerships = Partnership.query.filter(
                ((Partnership.requester_id == user_id) | 
                 (Partnership.partner_id == user_id)) &
                (Partnership.status.in_(['active', 'pending']))
            ).all()
            
            # Get IDs of users already partnered with
            partnered_user_ids = set()
            for partnership in existing_partnerships:
                if partnership.requester_id == user_id:
                    partnered_user_ids.add(partnership.partner_id)
                else:
                    partnered_user_ids.add(partnership.requester_id)
            
            # Filter available partners based on role restrictions
            available_partners = []
            for potential_partner in all_users:
                if potential_partner.id not in partnered_user_ids:
                    # Check if partnership is allowed
                    partnership_type = PartnershipValidator.get_allowed_partnership_types(
                        user_role, potential_partner.role
                    )
                    
                    if partnership_type:
                        partner_data = potential_partner.to_public_dict()
                        partner_data['allowedPartnershipType'] = partnership_type
                        available_partners.append(partner_data)
            
            return available_partners
            
        except Exception as e:
            print(f"Error getting available partners: {str(e)}")
            return []
    
    @staticmethod
    def get_partnership_rules():
        """
        Get the partnership rules for display in the frontend
        """
        return {
            'manufacturer': {
                'can_partner_with': ['distributor'],
                'description': 'Manufacturers can only partner with Distributors'
            },
            'distributor': {
                'can_partner_with': ['manufacturer', 'retailer'],
                'description': 'Distributors can partner with Manufacturers and Retailers'
            },
            'retailer': {
                'can_partner_with': ['distributor'],
                'description': 'Retailers can only partner with Distributors'
            }
        }
