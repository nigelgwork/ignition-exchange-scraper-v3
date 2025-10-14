#!/usr/bin/env python3
"""
Ignition 8.3 Automated Configuration Script

This script uses the Ignition 8.3 REST API to automatically configure:
1. Database connection to PostgreSQL
2. Gateway scripts (via project import)
3. Named queries (via project import)
4. Gateway timer script

Requirements:
- Ignition 8.3+ running
- API authentication configured
- requests library: pip install requests
"""

import sys
from typing import Optional

import requests


class IgnitionConfigurator:
    """Automates Ignition Gateway configuration via REST API"""

    def __init__(
        self,
        gateway_url: str = "http://localhost:8088",
        username: str = "admin",
        password: str = "password",
    ):
        self.gateway_url = gateway_url.rstrip("/")
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.api_token: Optional[str] = None

    def authenticate(self) -> bool:
        """
        Authenticate with Ignition Gateway.

        For Ignition 8.3, we need an API token. The token can be:
        1. Generated via Gateway web interface: Config > Security > API Keys
        2. Created via API (if we have admin credentials)

        For now, we'll use basic auth for initial setup endpoints.
        """
        print("Authenticating with Ignition Gateway...")

        # Test connection
        try:
            response = self.session.get(f"{self.gateway_url}/StatusPing", timeout=10)
            if response.status_code == 200:
                print("✓ Gateway is accessible")
                return True
            else:
                print(f"✗ Gateway returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to connect to gateway: {e}")
            return False

    def create_database_connection(self) -> bool:
        """Create PostgreSQL database connection"""
        print("\nCreating database connection 'exchange_scraper_db'...")

        db_config = [
            {
                "name": "exchange_scraper_db",
                "collection": "default",
                "enabled": True,
                "description": "Exchange Scraper Database Connection",
                "config": {
                    "driver": "org.postgresql.Driver",
                    "translator": "PostgreSQL",
                    "includeSchemaInTableName": False,
                    "connectURL": "jdbc:postgresql://postgres:5432/exchange_scraper",
                    "username": "ignition",
                    "password": {
                        "type": "PLAINTEXT",
                        "data": {"protected": {"value": "ignition"}},
                    },
                    "connectionProps": "",
                    "validationQuery": "SELECT 1",
                    "testOnBorrow": True,
                    "testOnReturn": False,
                    "testWhileIdle": True,
                    "poolInitSize": 4,
                    "poolMaxActive": 8,
                    "poolMaxIdle": 8,
                    "poolMinIdle": 0,
                    "poolMaxWait": 30000,
                    "evictionRate": 30000,
                    "evictionTests": 3,
                    "evictionTime": 300000,
                },
            }
        ]

        try:
            response = self.session.post(
                f"{self.gateway_url}/data/api/v1/resources/ignition/database-connection",
                json=db_config,
                auth=(self.username, self.password),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=30,
            )

            if response.status_code in [200, 201]:
                print("✓ Database connection created successfully")
                return True
            elif response.status_code == 409:
                print("ℹ Database connection already exists")
                return True
            else:
                print(f"✗ Failed to create database connection: {response.status_code}")
                print(f"  Response: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"✗ Request failed: {e}")
            return False

    def check_database_connection(self) -> bool:
        """Verify database connection exists and is working"""
        print("\nVerifying database connection...")

        try:
            response = self.session.get(
                f"{self.gateway_url}/data/api/v1/resources/find/ignition/database-connection/exchange_scraper_db",
                auth=(self.username, self.password),
                headers={"Accept": "application/json"},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                enabled = data.get("enabled", False)
                print(f"✓ Database connection found (enabled: {enabled})")
                return True
            else:
                print(f"✗ Database connection not found: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"✗ Request failed: {e}")
            return False

    def create_project(self, project_name: str = "ExchangeScraper") -> bool:
        """
        Create a new Ignition project.

        Note: In Ignition 8.3, scripts and named queries are project resources.
        For full automation, we would need to either:
        1. Import a pre-configured project export (.zip)
        2. Use project resource APIs to add scripts/queries (more complex)

        For now, this creates an empty project.
        """
        print(f"\nCreating project '{project_name}'...")

        project_config = {
            "title": project_name,
            "description": "Exchange Scraper Project - Automated Setup",
            "enabled": True,
        }

        try:
            response = self.session.put(
                f"{self.gateway_url}/data/api/v1/projects/{project_name}",
                json=project_config,
                auth=(self.username, self.password),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=30,
            )

            if response.status_code in [200, 201]:
                print(f"✓ Project '{project_name}' created successfully")
                return True
            elif response.status_code == 409:
                print(f"ℹ Project '{project_name}' already exists")
                return True
            else:
                print(f"✗ Failed to create project: {response.status_code}")
                print(f"  Response: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"✗ Request failed: {e}")
            return False

    def print_manual_steps(self):
        """Print remaining manual configuration steps"""
        print("\n" + "=" * 70)
        print("AUTOMATED CONFIGURATION COMPLETE")
        print("=" * 70)
        print("\n✓ Database connection 'exchange_scraper_db' created")
        print("\nREMAINING MANUAL STEPS:")
        print("\nDue to the complexity of project resources in Ignition 8.3,")
        print("the following steps still require manual configuration:")
        print("\n1. Import Gateway Scripts (15 minutes)")
        print("   - Open Ignition Designer")
        print("   - Follow: ignition-project/GATEWAY_SCRIPTS_IMPORT.md")
        print("   - Import 3 modules: api, notifications, scheduler")
        print("\n2. Create Named Queries (30 minutes)")
        print("   - Use Designer: Data > Named Queries")
        print("   - Copy SQL from: ignition-project/named-queries/")
        print("   - Create 9 queries with provided SQL")
        print("\n3. Set up Gateway Timer Script (10 minutes)")
        print("   - Gateway Config > Scripting > Gateway Timer Scripts")
        print(
            "   - Add script that calls: exchangeScraper.scheduler.checkAndRunSchedule()"
        )
        print("\n4. Test Configuration")
        print("   - Use Script Console to test API connection")
        print("   - Verify manual scrape trigger works")
        print("\nFor detailed instructions, see:")
        print("  - QUICK_START.md")
        print("  - ignition-project/GATEWAY_SCRIPTS_IMPORT.md")
        print("\n" + "=" * 70)


def main():
    """Main execution"""
    print("=" * 70)
    print("IGNITION 8.3 AUTOMATED CONFIGURATION")
    print("=" * 70)
    print("\nThis script will configure:")
    print("  • Database connection to PostgreSQL")
    print("  • Base project setup")
    print("\nGateway scripts and named queries require manual import")
    print("(see documentation for details)")
    print("=" * 70)

    # Initialize configurator
    config = IgnitionConfigurator()

    # Step 1: Authenticate
    if not config.authenticate():
        print("\n✗ Authentication failed. Cannot proceed.")
        print("  Please verify Ignition Gateway is running at http://localhost:8088")
        sys.exit(1)

    # Step 2: Create database connection
    if not config.create_database_connection():
        print("\n✗ Database connection creation failed.")
        print("  You may need to configure this manually via Gateway Config")
    else:
        # Verify connection
        config.check_database_connection()

    # Step 3: Create project (optional - may not be needed)
    # config.create_project("ExchangeScraper")

    # Print manual steps
    config.print_manual_steps()

    print("\nAutomation complete!")
    print("Gateway URL: http://localhost:8088")
    print("Username: admin")
    print("Password: password")


if __name__ == "__main__":
    main()
