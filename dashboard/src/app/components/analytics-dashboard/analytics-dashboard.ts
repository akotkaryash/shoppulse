import { Component, inject, OnInit } from '@angular/core';
import { AnalyticsService } from '../../services/analytics';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-analytics-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './analytics-dashboard.html',
  styleUrl: './analytics-dashboard.scss'
})
export class AnalyticsDashboardComponent implements OnInit {
  private analyticsService: AnalyticsService = inject(AnalyticsService);
  metrics: any = null;
  loading: boolean = true;

  ngOnInit(): void {
    this.analyticsService.getLiveMetrics().subscribe({
      next: (data) => {
        this.metrics = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('API Connection Error:', err);
        this.loading = false;
      }
    });
  }
}