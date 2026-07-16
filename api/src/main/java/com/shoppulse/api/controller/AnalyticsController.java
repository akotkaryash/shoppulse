package com.shoppulse.api.controller;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class AnalyticsController {

    private final JdbcTemplate jdbcTemplate;

    public AnalyticsController(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @GetMapping("/revenue/daily")
    public List<Map<String, Object>> getDailyRevenue() {
        // Optimized query: No redundant join to dim_date since event_date is on the fact table
        String sql = """
            SELECT 
                date_key as event_date,
                SUM(amount) as total_revenue
            FROM marts.fact_events
            WHERE event_type = 'purchase'
            GROUP BY event_date
            ORDER BY event_date DESC
            LIMIT 30;
            """;
        
        return jdbcTemplate.queryForList(sql);
    }
}