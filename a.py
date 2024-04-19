from ldap3 import Server, Connection,MODIFY_DELETE,MODIFY_ADD
import hashlib

class LDAPManager:
    def __init__(self, server_url, admin_user, admin_password):
        self.server_url = server_url
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.server = Server(self.server_url)
        self.conn = Connection(self.server, user=self.admin_user, password=self.admin_password)

    def connect(self):
        try:
            if not self.conn.bind():
                print(f"LDAP connection failed: {self.conn.last_error}")
                return False
            print("LDAP connection successful.")
            return True
        except Exception as e:
            print(f"An error occurred while connecting to LDAP: {str(e)}")
            return False

    def disconnect(self):
        self.conn.unbind()
        print("LDAP connection closed.")

    def add_employee(self, employee_data):
        try:
            # Extract employee data
            employee_number = employee_data.get('employeeNumber')
            given_name = employee_data.get('givenName')
            surname = employee_data.get('surname')
            email = employee_data.get('mail')
            password=employee_data.get('password')

            # Construct DN for the new employee
            dn = f"employeeNumber={employee_number},ou=users,ou=system"
            
            # Prepare attributes for the new entry
            attributes = {
                'objectClass': ['inetOrgPerson'],
                'employeeNumber': employee_number,
                'cn': f"{given_name} {surname}",
                'sn': surname,
                'givenName': given_name,
                'mail': email,
                'userPassword': hashlib.sha256(password.encode()).hexdigest()
            }

            # Add the new entry
            self.conn.add(dn, attributes=attributes)
            print(f"Employee {given_name} {surname} added successfully.")
            
        except Exception as e:
            print(f"Failed to add employee: {str(e)}")

    def delete_employee(self, employee_number):
        try:
            # Construct DN for the employee to be deleted
            dn = f"employeeNumber={employee_number},ou=users,ou=system"
            
            # Delete the employee entry
            self.conn.delete(dn)
            
            print(f"Employee with employeeNumber {employee_number} deleted successfully.")
        except Exception as e:
            print(f"Failed to delete employee: {str(e)}")

    def move_user(self, user_cn, old_ou, new_ou):
        try:
            if not self.conn:
                self.connect()

            # Prepare the relative DN for the user
            relative_dn = f"cn={user_cn},{old_ou}"

            # Construct the new DN for the user
            new_dn = f"cn={user_cn},{new_ou}"

            # Perform the modify DN operation to move the user
            self.conn.modify_dn(relative_dn, new_dn)

            print(f"User '{user_cn}' moved successfully from '{old_ou}' to '{new_ou}'.")
        except Exception as e:
            print(f"Error moving user: {str(e)}")

    def show_all_users(self):
        try:
            # Search for all user entries
            self.conn.search(search_base='ou=users,ou=system',
                             search_filter='(objectClass=inetOrgPerson)',
                             attributes=['cn', 'mail', 'employeeNumber'])
            print("All Users:")
            for entry in self.conn.entries:
                print(f"DN: {entry.entry_dn}")
                for attr, val in entry.entry_attributes_as_dict.items():
                    print(f"{attr}: {val}")
        except Exception as e:
            print(f"Failed to show all users: {str(e)}")

    def create_group(self, group_name):
        try:
            if not self.connect():
                return False

            # Define the DN for the group
            group_dn = f"cn={group_name},ou=Groups,dc=example,dc=com"
            
            # Define the group attributes
            group_attrs = {
                'objectClass': ['posixGroup'],
                'cn': group_name,
                
            }

            # Add the group entry
            self.conn.add(group_dn, attributes=group_attrs)
            
            print(f"Group {group_name} created successfully.")
            return True
        except Exception as e:
            print(f"Failed to create group: {str(e)}")
            
        

    def add_user_to_group(self, group_name, user_dn):
        try:
            if not self.connect():
                return False

            # Define the DN for the group
            group_dn = f"cn={group_name},ou=Groups,dc=example,dc=com"
            
            # Modify the group entry to add the user
            self.conn.modify(group_dn, {'uniqueMember': [(MODIFY_ADD, [user_dn])]})
            
            print(f"User {user_dn} added to group {group_name} successfully.")
            return True
        except Exception as e:
            print(f"Failed to add user to group: {str(e)}")
           

    def remove_user_from_group(self, group_name, user_dn):
        try:
            if not self.connect():
                return False

            # Define the DN for the group
            group_dn = f"cn={group_name},ou=Groups,dc=example,dc=com"
            
            # Modify the group entry to remove the user
            self.conn.modify(group_dn, {'uniqueMember': [(MODIFY_DELETE, [user_dn])]})
            
            print(f"User {user_dn} removed from group {group_name} successfully.")
            return True
        except Exception as e:
            print(f"Failed to remove user from group: {str(e)}")
           

# Example usage
if __name__ == "__main__":
    ldap_manager = LDAPManager('localhost:10389', 'uid=admin,ou=system', 'secret')
    if ldap_manager.connect():
        # Add a new employee
        new_employee_data = {
            'employeeNumber': '12345',
            'givenName': 'John',
            'surname': 'Doe',
            'mail': 'john.doe@example.com',
            'password':'Akash@1998'
        }
        # ldap_manager.add_employee(new_employee_data)
        

        # Delete an existing employee
        # employee_number_to_delete = '12344'
        # ldap_manager.delete_employee(employee_number_to_delete)

        # Show all users
        # ldap_manager.show_all_users()

        #moving user from one ou to another ou
        ldap_manager.move_user(user_cn='Rakesh Kumar', old_ou='ou=users,ou=system', new_ou='ou=transfeers,ou=system')


        # ldap_manager.disconnect()

        # ldap_manager.create_group('OILC')



