SELECT home_team_coverage.match_id as match_id, 
(SELECT scheduled FROM matches WHERE id = home_team_coverage.match_id) as scheduled,
(SELECT full_name FROM teams WHERE stats_id = home_team_coverage.stats_id) as home_team, 
(SELECT id FROM teams WHERE stats_id = home_team_coverage.stats_id) as home_id,
home_team_coverage.formation as home_formation, 
home_team_coverage.score as home_score, 
(CASE home_team_coverage.winner WHEN 0 then 0
	WHEN 1 then 3
	ELSE 1
    END) as home_points, 
home_team_coverage.first_half_score as home_first_half_score, 
home_team_coverage.second_half_score as home_second_half_score, 
home_team_coverage.attacks as home_attacks, 
home_team_coverage.ball_safe home_ball_safe, 
home_team_coverage.corner_kicks as home_corner_kicks, 
home_team_coverage.dangerous_attacks as home_dangerous_attacks, 
home_team_coverage.fouls as home_fouls, 
home_team_coverage.offsides as home_offsides, 
home_team_coverage.yellow_card as home_yellow_card, 
home_team_coverage.shots_on_target as home_shots_on_target, 
home_team_coverage.shots_total as home_shots_total, 
home_team_coverage.possessions as home_possession, 
(SELECT full_name FROM teams WHERE stats_id = away_team_coverage.stats_id) as away_team, 
(SELECT id FROM teams WHERE stats_id = away_team_coverage.stats_id) as away_id, 
away_team_coverage.formation as away_formation, 
away_team_coverage.score as away_score, 
(CASE away_team_coverage.winner WHEN 0 then 0
	WHEN 1 then 3
	ELSE 1
    END) as away_points, 
away_team_coverage.first_half_score as away_first_half_score, 
away_team_coverage.second_half_score as away_second_half_score, 
away_team_coverage.attacks as away_attacks, 
away_team_coverage.ball_safe as away_ball_safe, 
away_team_coverage.corner_kicks as away_corner_kicks, 
away_team_coverage.dangerous_attacks as away_dangerous_attacks, 
away_team_coverage.fouls as away_fouls, 
away_team_coverage.offsides as away_offsides, 
away_team_coverage.yellow_card as away_yellow_card, 
away_team_coverage.shots_on_target as away_shots_on_target, 
away_team_coverage.shots_total as away_shots_total, 
away_team_coverage.possessions  as away_possession
FROM home_team_coverage, 
away_team_coverage WHERE home_team_coverage.match_id = away_team_coverage.match_id;