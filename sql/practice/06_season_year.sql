DROP VIEW IF EXISTS v_matches_season_clean;

CREATE VIEW v_matches_season_clean AS
SELECT
    *,
    season AS season_year
FROM v_matches_clean;