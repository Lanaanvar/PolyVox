import os
import uuid
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Union, Dict, Any
from datetime import datetime
import logging
import json
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FileManager:
    """Utility class for file operations"""
    
    def __init__(self, base_dir: str = "temp"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def create_temp_file(self, suffix: str = "", prefix: str = "temp_") -> str:
        """Create a temporary file and return its path"""
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=suffix, 
            prefix=prefix,
            dir=self.base_dir
        )
        temp_file.close()
        return temp_file.name
    
    def create_unique_filename(self, original_filename: str) -> str:
        """Create a unique filename based on original filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        name, ext = os.path.splitext(original_filename)
        return f"{name}_{timestamp}_{unique_id}{ext}"
    
    def ensure_directory(self, directory: Union[str, Path]) -> Path:
        """Ensure directory exists, create if not"""
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    
    def cleanup_file(self, file_path: Union[str, Path]) -> bool:
        """Safely delete a file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Error cleaning up file {file_path}: {e}")
            return False
    
    def get_file_size(self, file_path: Union[str, Path]) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            logger.error(f"Error getting file size for {file_path}: {e}")
            return 0
    
    def validate_file_extension(self, filename: str, allowed_extensions: list) -> bool:
        """Validate file extension"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in [f".{ext}" if not ext.startswith(".") else ext for ext in allowed_extensions]

class AudioUtils:
    """Utility class for audio processing"""
    
    @staticmethod
    def get_audio_duration(file_path: str) -> float:
        """Get audio duration in seconds"""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0  # Convert to seconds
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return 0.0
    
    @staticmethod
    def convert_audio_format(input_path: str, output_path: str, format: str = "wav") -> bool:
        """Convert audio to specified format"""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(input_path)
            audio.export(output_path, format=format)
            return True
        except Exception as e:
            logger.error(f"Error converting audio format: {e}")
            return False
    
    @staticmethod
    def normalize_audio(input_path: str, output_path: str) -> bool:
        """Normalize audio levels"""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(input_path)
            normalized = audio.normalize()
            normalized.export(output_path, format="wav")
            return True
        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            return False

class VideoUtils:
    """Utility class for video processing"""
    
    @staticmethod
    def get_video_info(file_path: str) -> Dict[str, Any]:
        """Get video information"""
        try:
            import ffmpeg
            probe = ffmpeg.probe(file_path)
            video_info = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
                None
            )
            audio_info = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'audio'),
                None
            )
            
            return {
                'duration': float(probe['format']['duration']),
                'size': int(probe['format']['size']),
                'video': video_info,
                'audio': audio_info
            }
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {}

class JobManager:
    """Utility class for managing processing jobs"""
    
    def __init__(self):
        self.jobs = {}
    
    def create_job(self, job_type: str = "dubbing") -> str:
        """Create a new job and return job ID"""
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            'id': job_id,
            'type': job_type,
            'status': 'pending',
            'progress': 0.0,
            'current_step': 'initialization',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'error_message': None
        }
        return job_id
    
    def update_job(self, job_id: str, **kwargs) -> bool:
        """Update job status"""
        if job_id not in self.jobs:
            return False
        
        self.jobs[job_id].update(kwargs)
        self.jobs[job_id]['updated_at'] = datetime.now().isoformat()
        return True
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job information"""
        return self.jobs.get(job_id)
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a job"""
        if job_id in self.jobs:
            del self.jobs[job_id]
            return True
        return False

class ValidationUtils:
    """Utility class for validation"""
    
    @staticmethod
    def validate_file_size(file_path: str, max_size_mb: int = 100) -> bool:
        """Validate file size"""
        try:
            file_size = os.path.getsize(file_path)
            max_size_bytes = max_size_mb * 1024 * 1024
            return file_size <= max_size_bytes
        except Exception:
            return False
    
    @staticmethod
    def validate_audio_file(file_path: str) -> bool:
        """Validate audio file"""
        try:
            from pydub import AudioSegment
            AudioSegment.from_file(file_path)
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_video_file(file_path: str) -> bool:
        """Validate video file"""
        try:
            import ffmpeg
            ffmpeg.probe(file_path)
            return True
        except Exception:
            return False

class ErrorHandler:
    """Utility class for error handling"""
    
    @staticmethod
    def handle_service_error(service_name: str, error: Exception) -> Dict[str, Any]:
        """Handle service errors and return formatted response"""
        error_message = str(error)
        logger.error(f"Error in {service_name}: {error_message}")
        
        return {
            'success': False,
            'error': f"{service_name} error: {error_message}",
            'service': service_name,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def log_processing_step(job_id: str, step: str, status: str = "started"):
        """Log processing step"""
        logger.info(f"Job {job_id} - {step}: {status}")

def generate_hash(data: str) -> str:
    """Generate MD5 hash for data"""
    return hashlib.md5(data.encode()).hexdigest()

def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

# Global instances
file_manager = FileManager()
job_manager = JobManager()