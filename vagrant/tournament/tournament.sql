-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;

-- create database
create database tournament;

-- connect to the nnewly created database
\c tournament;

-- create database tables
-- table: Players
create table players (
	id serial primary key,
	name text
);

-- table: Match Results
create table match_results (
	winner integer references players(id),
	loser integer references players(id),
	primary key (winner, loser)
);

-- create views
create or replace view player_standings as
	select players.id as id, players.name as name, count(win_results.*) as wins, count(all_results.*) as matches
	from players
	left join match_results as win_results
	on players.id = win_results.winner
	left join match_results as all_results
	on players.id = all_results.winner
	or players.id = all_results.loser
	group by players.id
	order by wins DESC;

create or replace view players_played_with as
	select players.id as player_id, match_results.loser as opponent
	from players, match_results
	where players.id = match_results.winner
	UNION
	select players.id as player_id, match_results.winner as opponent
	from players, match_results
	where players.id = match_results.loser
	ORDER BY player_id
