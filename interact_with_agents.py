#!/usr/bin/env python3
"""
Interactive Terry Delmonaco Manager Agent Interface
Version: 3.2
Description: Direct interaction with the automation agent ecosystem
"""

import asyncio
import json
import requests
from typing import Dict, Any
from datetime import datetime


class TerryDelmonacoInterface:
    """Interactive interface for Terry Delmonaco Manager Agent."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        try:
            response = self.session.get(f"{self.base_url}/")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_health(self) -> Dict[str, Any]:
        """Get system health."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def delegate_task(self, task_type: str, priority: str = "medium", data: Dict = None) -> Dict[str, Any]:
        """Delegate a task to the appropriate agent."""
        try:
            payload = {
                "task_type": task_type,
                "priority": priority,
                "data": data or {}
            }
            response = self.session.post(f"{self.base_url}/tasks/delegate", json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def send_cursor_task(self, task_type: str, content: str, priority: str = "medium") -> Dict[str, Any]:
        """Send a task to the Cursor Agent."""
        try:
            payload = {
                "type": task_type,
                "content": content,
                "priority": priority
            }
            response = self.session.post(f"{self.base_url}/cursor/task", json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report."""
        try:
            response = self.session.get(f"{self.base_url}/status/report")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def record_screen_activity(self) -> Dict[str, Any]:
        """Trigger screen activity recording."""
        try:
            response = self.session.post(f"{self.base_url}/screen/record")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def sync_learnings(self) -> Dict[str, Any]:
        """Sync learnings with CESAR ecosystem."""
        try:
            response = self.session.post(f"{self.base_url}/learnings/sync")
            return response.json()
        except Exception as e:
            return {"error": str(e)}


def print_menu():
    """Print the interactive menu."""
    print("\n" + "="*60)
    print("🤖 TERRY DELMONACO MANAGER AGENT INTERFACE")
    print("="*60)
    print("1.  Get System Status")
    print("2.  Get Health Check")
    print("3.  Delegate Task")
    print("4.  Send Cursor Task")
    print("5.  Get Status Report")
    print("6.  Record Screen Activity")
    print("7.  Sync Learnings")
    print("8.  Run Code Review")
    print("9.  Run Bug Fix")
    print("10. Run Documentation Task")
    print("11. Run Security Scan")
    print("12. Exit")
    print("="*60)


def print_result(title: str, result: Dict[str, Any]):
    """Print formatted result."""
    print(f"\n📋 {title}")
    print("-" * 40)
    print(json.dumps(result, indent=2))
    print("-" * 40)


def main():
    """Main interactive interface."""
    interface = TerryDelmonacoInterface()
    
    print("🚀 Starting Terry Delmonaco Manager Agent Interface...")
    
    while True:
        print_menu()
        choice = input("\nEnter your choice (1-12): ").strip()
        
        try:
            if choice == "1":
                result = interface.get_system_status()
                print_result("System Status", result)
                
            elif choice == "2":
                result = interface.get_health()
                print_result("Health Check", result)
                
            elif choice == "3":
                task_type = input("Enter task type (automated_reporting, inbox_calendar, etc.): ").strip()
                priority = input("Enter priority (low, medium, high): ").strip() or "medium"
                data = input("Enter additional data (JSON format, optional): ").strip()
                
                task_data = {}
                if data:
                    try:
                        task_data = json.loads(data)
                    except:
                        print("❌ Invalid JSON format")
                        continue
                
                result = interface.delegate_task(task_type, priority, task_data)
                print_result("Task Delegation", result)
                
            elif choice == "4":
                task_type = input("Enter task type (code_review, bug_fix, etc.): ").strip()
                content = input("Enter content: ").strip()
                priority = input("Enter priority (low, medium, high): ").strip() or "medium"
                
                result = interface.send_cursor_task(task_type, content, priority)
                print_result("Cursor Task", result)
                
            elif choice == "5":
                result = interface.get_status_report()
                print_result("Status Report", result)
                
            elif choice == "6":
                result = interface.record_screen_activity()
                print_result("Screen Activity Recording", result)
                
            elif choice == "7":
                result = interface.sync_learnings()
                print_result("Learning Sync", result)
                
            elif choice == "8":
                code = input("Enter code to review: ").strip()
                result = interface.send_cursor_task("code_review", code, "high")
                print_result("Code Review", result)
                
            elif choice == "9":
                bug_description = input("Enter bug description: ").strip()
                result = interface.send_cursor_task("bug_fix", bug_description, "high")
                print_result("Bug Fix", result)
                
            elif choice == "10":
                doc_request = input("Enter documentation request: ").strip()
                result = interface.send_cursor_task("documentation", doc_request, "medium")
                print_result("Documentation Task", result)
                
            elif choice == "11":
                security_request = input("Enter security scan request: ").strip()
                result = interface.send_cursor_task("system_analysis", security_request, "high")
                print_result("Security Scan", result)
                
            elif choice == "12":
                print("👋 Goodbye! Terry Delmonaco Manager Agent shutting down...")
                break
                
            else:
                print("❌ Invalid choice. Please enter a number between 1-12.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 