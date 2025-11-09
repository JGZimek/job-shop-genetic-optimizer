import csv
from datetime import datetime
from pathlib import Path


class ScheduleExporter:
    """Eksportuj harmonogram do różnych formatów"""
    
    @staticmethod
    def export_to_csv(instance, solution, output_path=None):
        """Eksportuj do CSV"""
        if output_path is None:
            output_path = Path("schedules") / f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Job', 'Operation', 'Machine', 'Start Time', 'Duration', 'End Time'])
            
            for i, (job_id, op_id) in enumerate(solution.operation_sequence):
                start_time = solution.start_times[i]
                operation = instance.jobs[job_id].operations[op_id]
                duration = operation.processing_time
                end_time = start_time + duration
                
                writer.writerow([
                    f'J{job_id}',
                    f'O{op_id}',
                    f'M{operation.machine_id}',
                    f'{start_time:.2f}',
                    f'{duration:.2f}',
                    f'{end_time:.2f}'
                ])
        
        return output_path
    
    @staticmethod
    def export_to_json(instance, solution, output_path=None):
        """Eksportuj do JSON"""
        import json
        
        if output_path is None:
            output_path = Path("schedules") / f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path.parent.mkdir(exist_ok=True)
        
        makespan = max([solution.start_times[i] + instance.jobs[job_id].operations[op_id].processing_time 
                       for i, (job_id, op_id) in enumerate(solution.operation_sequence)])
        
        schedule_data = {
            'makespan': makespan,
            'jobs': len(instance.jobs),
            'machines': instance.num_machines,
            'operations': []
        }
        
        for i, (job_id, op_id) in enumerate(solution.operation_sequence):
            start_time = solution.start_times[i]
            operation = instance.jobs[job_id].operations[op_id]
            
            schedule_data['operations'].append({
                'job_id': int(job_id),
                'operation_id': int(op_id),
                'machine_id': int(operation.machine_id),
                'start_time': float(start_time),
                'duration': float(operation.processing_time),
                'end_time': float(start_time + operation.processing_time)
            })
        
        with open(output_path, 'w') as f:
            json.dump(schedule_data, f, indent=2)
        
        return output_path
    
    @staticmethod
    def export_gantt_image(fig, output_path=None):
        """Eksportuj Gantt do PNG"""
        if output_path is None:
            output_path = Path("schedules") / f"gantt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        output_path.parent.mkdir(exist_ok=True)
        fig.savefig(output_path, dpi=150, facecolor='#1a1a1a')
        
        return output_path
