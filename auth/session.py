class Session:
    _instance = None
    user = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Session()
        return cls._instance

    def set_user(self, user_data):
        self.user = user_data

    def get_user(self):
        return self.user

    def get_role(self):
        if not self.user:
            return 'owner' # Default to owner if session is unauthenticated in dev mode
        role = self.user.get('role', 'owner')
        return role if role in ['owner', 'manager', 'staff'] else 'owner'

    def is_owner(self):
        return self.get_role() == 'owner'

    def is_manager(self):
        return self.get_role() in ['owner', 'manager']

    def is_staff(self):
        return True

    def can_access_module(self, module_name):
        role = self.get_role()
        if role == 'owner':
            return True
        
        if role == 'manager':
            # Manager has access to all operational modules and reports, but restricted from Users & DB Maintenance
            restricted = ['Users', 'User Management', 'Database Maintenance', 'Danger Zone']
            return module_name not in restricted
            
        if role == 'staff':
            # Staff has access to core operations (Invoices, Purchases, Payments, Stock, Customers, Vendors, Items)
            allowed = ['Dashboard', 'Customers', 'Vendors', 'Items', 'Invoices', 'Purchases', 'Payments', 'Stock', 'About']
            return module_name in allowed
            
        return True

    def clear(self):
        self.user = None
