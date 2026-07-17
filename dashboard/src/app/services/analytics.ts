import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AnalyticsService {
  // Use the container name (api) because the frontend and api 
  // are on the same Docker network
  // private baseUrl = environment.apiBaseUrl;
  // dashboard/src/app/services/analytics.service.ts
  private baseUrl = '/api'; // The proxy will handle the redirect 

  constructor(private http: HttpClient) { }

  getLiveMetrics(): Observable<any> {
    return this.http.get(`${this.baseUrl}/metrics/live`);
  }
}