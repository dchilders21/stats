CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `home_away_coverage_ligue_1` AS
    SELECT 
        `home_team_coverage_ligue_1`.`match_id` AS `match_id`,
        (SELECT 
                `matches_ligue_1`.`scheduled`
            FROM
                `matches_ligue_1`
            WHERE
                (`matches_ligue_1`.`id` = `home_team_coverage_ligue_1`.`match_id`)) AS `scheduled`,
        (SELECT 
                `matches_ligue_1`.`round_number`
            FROM
                `matches_ligue_1`
            WHERE
                (`matches_ligue_1`.`id` = `home_team_coverage_ligue_1`.`match_id`)) AS `round`,
        (SELECT 
                `teams`.`full_name`
            FROM
                `teams`
            WHERE
                (`teams`.`stats_id` = `home_team_coverage_ligue_1`.`stats_id`)) AS `home_team`,
        (SELECT 
                `teams`.`id`
            FROM
                `teams`
            WHERE
                (`teams`.`stats_id` = `home_team_coverage_ligue_1`.`stats_id`)) AS `home_id`,
        `home_team_coverage_ligue_1`.`formation` AS `home_formation`,
        `home_team_coverage_ligue_1`.`score` AS `home_score`,
        (CASE `home_team_coverage_ligue_1`.`winner`
            WHEN 0 THEN 0
            WHEN 1 THEN 3
            ELSE 1
        END) AS `home_points`,
        `home_team_coverage_ligue_1`.`first_half_score` AS `home_first_half_score`,
        `home_team_coverage_ligue_1`.`second_half_score` AS `home_second_half_score`,
        `home_team_coverage_ligue_1`.`attacks` AS `home_attacks`,
        `home_team_coverage_ligue_1`.`ball_safe` AS `home_ball_safe`,
        `home_team_coverage_ligue_1`.`corner_kicks` AS `home_corner_kicks`,
        `home_team_coverage_ligue_1`.`dangerous_attacks` AS `home_dangerous_attacks`,
        `home_team_coverage_ligue_1`.`fouls` AS `home_fouls`,
        `home_team_coverage_ligue_1`.`offsides` AS `home_offsides`,
        `home_team_coverage_ligue_1`.`yellow_card` AS `home_yellow_card`,
        `home_team_coverage_ligue_1`.`shots_on_target` AS `home_shots_on_target`,
        `home_team_coverage_ligue_1`.`shots_total` AS `home_shots_total`,
        `home_team_coverage_ligue_1`.`possessions` AS `home_possession`,
        (SELECT 
                `teams`.`full_name`
            FROM
                `teams`
            WHERE
                (`teams`.`stats_id` = `away_team_coverage`.`stats_id`)) AS `away_team`,
        (SELECT 
                `teams`.`id`
            FROM
                `teams`
            WHERE
                (`teams`.`stats_id` = `away_team_coverage_ligue_1`.`stats_id`)) AS `away_id`,
        `away_team_coverage_ligue_1`.`formation` AS `away_formation`,
        `away_team_coverage_ligue_1`.`score` AS `away_score`,
        (CASE `away_team_coverage_ligue_1`.`winner`
            WHEN 0 THEN 0
            WHEN 1 THEN 3
            ELSE 1
        END) AS `away_points`,
        `away_team_coverage_ligue_1`.`first_half_score` AS `away_first_half_score`,
        `away_team_coverage_ligue_1`.`second_half_score` AS `away_second_half_score`,
        `away_team_coverage_ligue_1`.`attacks` AS `away_attacks`,
        `away_team_coverage_ligue_1`.`ball_safe` AS `away_ball_safe`,
        `away_team_coverage_ligue_1`.`corner_kicks` AS `away_corner_kicks`,
        `away_team_coverage_ligue_1`.`dangerous_attacks` AS `away_dangerous_attacks`,
        `away_team_coverage_ligue_1`.`fouls` AS `away_fouls`,
        `away_team_coverage_ligue_1`.`offsides` AS `away_offsides`,
        `away_team_coverage_ligue_1`.`yellow_card` AS `away_yellow_card`,
        `away_team_coverage_ligue_1`.`shots_on_target` AS `away_shots_on_target`,
        `away_team_coverage_ligue_1`.`shots_total` AS `away_shots_total`,
        `away_team_coverage_ligue_1`.`possessions` AS `away_possession`
    FROM
        (`home_team_coverage_ligue_1`
        JOIN `away_team_coverage_ligue_1`)
    WHERE
        (`home_team_coverage_ligue_1`.`match_id` = `away_team_coverage_ligue_1`.`match_id`)