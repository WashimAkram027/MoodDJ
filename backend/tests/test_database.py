import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.database import execute_query, get_db_connection


class TestDatabase:
    """Unit tests for Database module"""
    
    def test_database_connection(self):
        """
        Test Case 1: Database Connection
        
        Purpose: Verify database connection can be established
        Input: None
        Expected Output: Valid database connection object
        Tests: Database connectivity
        """
        conn = get_db_connection()
        assert conn is not None
        assert conn.is_connected()
        conn.close()
        print("✅ Test 1 PASSED: Database connection successful")
    
    def test_execute_query_select(self):
        """
        Test Case 2: SELECT Query Execution
        
        Purpose: Verify SELECT queries work correctly
        Input: "SELECT COUNT(*) as count FROM songs"
        Expected Output: List with count >= 0
        Tests: Read operations from database
        """
        query = "SELECT COUNT(*) as count FROM songs"
        result = execute_query(query, fetch=True)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'count' in result[0]
        assert result[0]['count'] >= 0
        print(f"✅ Test 2 PASSED: Found {result[0]['count']} songs in database")
    
    def test_execute_query_insert_delete(self):
        """
        Test Case 3: INSERT and DELETE Operations
        
        Purpose: Verify database write and delete operations
        Input: Test mood session data
        Expected Output: Successfully inserted and deleted record
        Tests: Write operations, data integrity, cleanup
        """
        # Insert test data
        insert_query = """
            INSERT INTO mood_sessions (user_id, detected_mood, confidence_score)
            VALUES (%s, %s, %s)
        """
        session_id = execute_query(insert_query, (1, 'test_mood', 0.99))
        
        assert session_id is not None
        assert session_id > 0
        print(f"✅ Test 3a PASSED: Inserted test record with ID {session_id}")
        
        # Verify insert
        select_query = "SELECT * FROM mood_sessions WHERE session_id = %s"
        result = execute_query(select_query, (session_id,), fetch=True)
        
        assert len(result) == 1
        assert result[0]['detected_mood'] == 'test_mood'
        assert result[0]['confidence_score'] == 0.99
        print("✅ Test 3b PASSED: Verified inserted data")
        
        # Clean up - delete test data
        delete_query = "DELETE FROM mood_sessions WHERE session_id = %s"
        execute_query(delete_query, (session_id,))
        
        # Verify deletion
        verify_query = "SELECT * FROM mood_sessions WHERE session_id = %s"
        result = execute_query(verify_query, (session_id,), fetch=True)
        assert len(result) == 0
        print("✅ Test 3c PASSED: Test data cleaned up")
    
    def test_parameterized_query_sql_injection_prevention(self):
        """
        Test Case 4: SQL Injection Prevention
        
        Purpose: Verify that parameterized queries prevent SQL injection
        Input: Malicious SQL string as parameter
        Expected Output: No SQL injection, treated as literal string
        Tests: Security - SQL injection prevention
        """
        # Attempt SQL injection
        malicious_input = "'; DROP TABLE songs; --"
        
        query = "SELECT * FROM songs WHERE title = %s"
        result = execute_query(query, (malicious_input,), fetch=True)
        
        # Should return empty list (no match), not execute the DROP TABLE
        assert isinstance(result, list)
        
        # Verify songs table still exists
        verify_query = "SELECT COUNT(*) as count FROM songs"
        verify_result = execute_query(verify_query, fetch=True)
        assert verify_result is not None
        print("✅ Test 4 PASSED: SQL injection prevented")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])