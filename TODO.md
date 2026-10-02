# TODO

- Game mode enum: reorganise ServerAcceptedType into GAMEMODE_XXX constants covering every stat-bearing activity, including boss fights, before real match data exists. The database API carries it as ServerAcceptedType until then.
- Database services for the remaining data areas, in the matchmaker's order: shop and cosmetics, achievements and titles and XP, loadouts and settings, friends and roles, ranked and parkour. One proto file per area under `database/`.
- GetAllPlayerStats: every mode's PlayerStats for one player and season in one call, for the trainer card.
- A client-streaming RecordMatch beside the unary one if servers need to replay a backlog of windows.
- Player movement: a matchmaker service for transfer, queue, leave and rejoin, and a proxy-hosted TransferPlayer service plus session events so the matchmaker knows which proxy holds a player.
