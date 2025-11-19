"""Repository for background jobs"""
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
from .base_repository import BaseRepository


class JobRepository(BaseRepository):
    """Repository for managing background jobs in database"""

    def create(self, job_data: Dict) -> str:
        """
        Create a new job

        Args:
            job_data: Dictionary with job fields

        Returns:
            job_id of created job
        """
        # Serialize JSON fields
        if 'params' in job_data:
            job_data['params'] = self._serialize_json_field(job_data['params'])
        if 'result' in job_data:
            job_data['result'] = self._serialize_json_field(job_data['result'])

        # Add creation timestamp
        if 'created_at' not in job_data:
            job_data['created_at'] = datetime.utcnow().isoformat()

        self.insert('job_queue', job_data)
        return job_data['job_id']

    def get_by_job_id(self, job_id: str) -> Optional[Dict]:
        """Get job by job_id"""
        job = self.fetchone(
            "SELECT * FROM job_queue WHERE job_id = ?",
            (job_id,)
        )
        if job:
            return self._deserialize_job(job)
        return None

    def list_jobs(
        self,
        job_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict:
        """
        List jobs with filters

        Returns:
            Dict with 'jobs' and 'total' keys
        """
        # Build WHERE clause
        where_clauses = []
        params = []

        if job_type:
            where_clauses.append("job_type = ?")
            params.append(job_type)

        if status:
            where_clauses.append("status = ?")
            params.append(status)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM job_queue {where_sql}"
        count_result = self.fetchone(count_query, tuple(params))
        total = count_result['count'] if count_result else 0

        # Get jobs
        query = f"""
            SELECT * FROM job_queue
            {where_sql}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        jobs = self.fetchall(query, tuple(params))
        jobs = [self._deserialize_job(job) for job in jobs]

        return {
            'jobs': jobs,
            'total': total,
            'limit': limit,
            'offset': offset
        }

    def update_job(self, job_id: str, updates: Dict) -> bool:
        """Update a job"""
        # Serialize JSON fields
        if 'params' in updates:
            updates['params'] = self._serialize_json_field(updates['params'])
        if 'result' in updates:
            updates['result'] = self._serialize_json_field(updates['result'])

        return self.update('job_queue', job_id, updates, id_column='job_id')

    def update_status(
        self,
        job_id: str,
        new_status: str,
        progress: Optional[int] = None,
        total: Optional[int] = None
    ) -> bool:
        """Update job status and optionally progress"""
        updates = {'status': new_status}

        if progress is not None:
            updates['progress'] = progress
        if total is not None:
            updates['total'] = total

        # Set timestamps based on status
        if new_status == 'running' and 'started_at' not in updates:
            updates['started_at'] = datetime.utcnow().isoformat()
        elif new_status in ['completed', 'failed']:
            updates['completed_at'] = datetime.utcnow().isoformat()

        return self.update_job(job_id, updates)

    def set_job_result(self, job_id: str, result: Dict) -> bool:
        """Set job result"""
        return self.update_job(job_id, {
            'result': result,
            'status': 'completed',
            'completed_at': datetime.utcnow().isoformat()
        })

    def set_job_error(self, job_id: str, error: str) -> bool:
        """Set job error"""
        return self.update_job(job_id, {
            'error': error,
            'status': 'failed',
            'completed_at': datetime.utcnow().isoformat()
        })

    def delete_job(self, job_id: str) -> bool:
        """Delete a job"""
        return self.delete('job_queue', job_id, id_column='job_id')

    def get_active_jobs(self) -> List[Dict]:
        """Get all queued or running jobs"""
        jobs = self.fetchall(
            """
            SELECT * FROM job_queue
            WHERE status IN ('queued', 'running')
            ORDER BY created_at ASC
            """
        )
        return [self._deserialize_job(job) for job in jobs]

    def get_recent_jobs(self, limit: int = 20) -> List[Dict]:
        """Get recent jobs"""
        jobs = self.fetchall(
            """
            SELECT * FROM job_queue
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,)
        )
        return [self._deserialize_job(job) for job in jobs]

    def cleanup_old_jobs(self, days: int = 7) -> int:
        """Delete completed jobs older than N days"""
        cutoff_date = datetime.utcnow().timestamp() - (days * 86400)

        self.execute(
            """
            DELETE FROM job_queue
            WHERE status IN ('completed', 'failed')
            AND created_at < ?
            """,
            (cutoff_date,)
        )
        return self.cursor.rowcount

    def get_statistics(self) -> Dict:
        """Get job statistics"""
        stats = self.fetchone("""
            SELECT
                COUNT(*) as total_jobs,
                COUNT(CASE WHEN status = 'queued' THEN 1 END) as queued_count,
                COUNT(CASE WHEN status = 'running' THEN 1 END) as running_count,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count
            FROM job_queue
        """)
        return dict(stats) if stats else {}

    def _deserialize_job(self, job: Dict) -> Dict:
        """Deserialize JSON fields in a job"""
        if not job:
            return job

        job_dict = dict(job)
        if 'params' in job_dict:
            job_dict['params'] = self._deserialize_json_field(job_dict['params'])
        if 'result' in job_dict:
            job_dict['result'] = self._deserialize_json_field(job_dict['result'])

        return job_dict
