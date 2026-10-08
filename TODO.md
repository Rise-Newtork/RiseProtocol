# TODO

- Database services for the remaining data areas, in the matchmaker's order: shop and cosmetics, achievements and titles and XP, loadouts and settings, friends and roles, ranked and parkour. One proto file per area under `database/`.
- GetAllPlayerStats: every mode's PlayerStats for one player and season in one call, for the trainer card.
- A client-streaming RecordMatch beside the unary one if servers need to replay a backlog of windows.
- Rejoin: a window in which a disconnected player's placement still points at their match, so login routing sends them back instead of to a hub. The rest of player movement landed in v1.15.0.
- PlayerDirectoryService: the network-wide player list and FindPlayer, still a proposal in RisePlugins/protocol-proposals.
- One GAMEMODE_BOSS per boss, once there is more than one: boards and lifetime twins are keyed by mode, so separate bosses need separate constants.
