from django.core.management.base import BaseCommand, CommandError
from app.services.user_service import UserService
import getpass

class Command(BaseCommand):
    help = 'Create an admin user for the application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Admin email address',
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Admin username',
        )
        parser.add_argument(
            '--first_name',
            type=str,
            help='Admin first name',
        )
        parser.add_argument(
            '--last_name',
            type=str,
            help='Admin last name',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Admin password (will prompt if not provided)',
        )
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Run in interactive mode (prompts for all fields)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Creating admin user...\n')
        )

        try:
            # Interactive mode - prompt for all fields
            if options['interactive']:
                email = input('Email: ')
                username = input('Username: ')
                first_name = input('First name: ')
                last_name = input('Last name: ')
                password = getpass.getpass('Password: ')
                confirm_password = getpass.getpass('Confirm password: ')
                
                if password != confirm_password:
                    raise CommandError('Passwords do not match')
            
            # Non-interactive mode - use provided arguments or prompt for missing ones
            else:
                email = options['email'] or input('Email: ')
                username = options['username'] or input('Username: ')
                first_name = options['first_name'] or input('First name: ')
                last_name = options['last_name'] or input('Last name: ')
                
                if options['password']:
                    password = options['password']
                else:
                    password = getpass.getpass('Password: ')
                    confirm_password = getpass.getpass('Confirm password: ')
                    if password != confirm_password:
                        raise CommandError('Passwords do not match')

            # Validate required fields
            if not all([email, username, first_name, last_name, password]):
                raise CommandError('All fields are required')

            # Create the admin user
            user = UserService.create_admin_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'\nAdmin user created successfully!\n'
                    f'Email: {user.email}\n'
                    f'Username: {user.username}\n'
                    f'Name: {user.first_name} {user.last_name}\n'
                    f'Staff: {user.is_staff}\n'
                    f'Superuser: {user.is_superuser}\n'
                )
            )

        except ValueError as e:
            raise CommandError(f'Error creating admin user: {str(e)}')
        except KeyboardInterrupt:
            self.stdout.write('\nOperation cancelled.')
        except Exception as e:
            raise CommandError(f'Unexpected error: {str(e)}')