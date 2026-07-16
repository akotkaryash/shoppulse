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
        String sql = """
            SELECT 
                date_key AS event_date,
                SUM(amount) AS total_revenue
            FROM marts.fact_events
            WHERE event_type = 'purchase'
            GROUP BY date_key
            ORDER BY date_key DESC
            LIMIT 30;
            """;
        return jdbcTemplate.queryForList(sql);
    }

    @GetMapping("/products/top")
    public List<Map<String, Object>> getTopProducts() {
        String sql = """
            SELECT 
                product_key,
                SUM(amount) AS total_revenue,
                SUM(quantity) AS total_sold
            FROM marts.fact_events
            WHERE event_type = 'purchase'
            GROUP BY product_key
            ORDER BY total_revenue DESC
            LIMIT 5;
        """;
        return jdbcTemplate.queryForList(sql);
    }

    @GetMapping("/funnel")
    public List<Map<String, Object>> getFunnel() { 
        String sql = """
            SELECT 
                event_type,
                COUNT(*) AS event_count
            FROM marts.fact_events
            GROUP BY event_type
            ORDER BY 
                CASE event_type
                    WHEN 'page_view' THEN 1
                    WHEN 'add_to_cart' THEN 2
                    WHEN 'purchase' THEN 3
                    ELSE 4
                END;
        """;
        return jdbcTemplate.queryForList(sql);
    }

    @GetMapping("/metrics/live") 
    public Map<String, Object> getLiveMetrics() {
        String sql = """
            SELECT 
                COUNT(*) AS total_events,
                SUM(CASE WHEN event_type = 'purchase' THEN amount ELSE 0 END) as total_revenue
            FROM marts.fact_events;
        """;
        return jdbcTemplate.queryForMap(sql); 
    }
}