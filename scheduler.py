#!/usr/bin/env python3
"""
Website Monitor Scheduler
Runs the monitoring checks at regular intervals in Docker environment.
"""

import time
import subprocess
import os
import logging
import signal
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/logs/scheduler.log')
    ]
)
logger = logging.getLogger(__name__)

class MonitorScheduler:
    def __init__(self):
        self.interval = int(os.getenv('MONITOR_INTERVAL', 3600))  # Default: 1 hour
        self.running = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)
        
    def handle_signal(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    def run_monitoring(self):
        """Execute the monitoring script."""
        try:
            logger.info('Starting website monitoring check...')
            start_time = datetime.now()
            
            # Run the main monitoring script
            result = subprocess.run(
                ['python', 'main.py'], 
                capture_output=True, 
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            if result.returncode == 0:
                logger.info(f'Monitoring completed successfully in {execution_time:.2f} seconds')
                if result.stdout:
                    logger.debug(f'Output: {result.stdout}')
            else:
                logger.error(f'Monitoring failed with exit code {result.returncode}')
                if result.stderr:
                    logger.error(f'Error output: {result.stderr}')
                if result.stdout:
                    logger.info(f'Standard output: {result.stdout}')
                    
        except subprocess.TimeoutExpired:
            logger.error('Monitoring timed out after 30 minutes')
        except Exception as e:
            logger.error(f'Error running monitoring: {e}')
            
    def start(self):
        """Start the scheduler main loop."""
        logger.info(f'🚀 Starting Website Monitor Scheduler')
        logger.info(f'📅 Monitoring interval: {self.interval} seconds ({self.interval/3600:.1f} hours)')
        logger.info(f'📁 Working directory: {os.getcwd()}')
        logger.info(f'🐍 Python version: {sys.version}')
        
        # Run initial monitoring check
        logger.info('Running initial monitoring check...')
        self.run_monitoring()
        
        # Main scheduling loop
        while self.running:
            try:
                logger.info(f'⏰ Waiting {self.interval} seconds until next monitoring run...')
                
                # Sleep in small intervals to allow for graceful shutdown
                sleep_remaining = self.interval
                while sleep_remaining > 0 and self.running:
                    sleep_time = min(60, sleep_remaining)  # Sleep max 60 seconds at a time
                    time.sleep(sleep_time)
                    sleep_remaining -= sleep_time
                
                if self.running:
                    self.run_monitoring()
                    
            except KeyboardInterrupt:
                logger.info('Scheduler interrupted by user')
                break
            except Exception as e:
                logger.error(f'Unexpected error in scheduler: {e}')
                time.sleep(60)  # Wait a minute before trying again
                
        logger.info('📊 Website Monitor Scheduler stopped')

def main():
    """Main entry point for the scheduler."""
    # Ensure logs directory exists
    os.makedirs('/app/logs', exist_ok=True)
    
    try:
        scheduler = MonitorScheduler()
        scheduler.start()
    except Exception as e:
        logger.error(f'Failed to start scheduler: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
