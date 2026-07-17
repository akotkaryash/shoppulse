import { Routes } from '@angular/router';
import { AnalyticsDashboardComponent } from './components/analytics-dashboard/analytics-dashboard';

export const routes: Routes = [
  { path: 'analytics', component: AnalyticsDashboardComponent },
  { path: '', redirectTo: '/analytics', pathMatch: 'full' }
];