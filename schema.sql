drop table if exists score;
create table score (
  id integer primary key autoincrement,
  username text not null,
  tags text null,
  starttime text not null,
  lasttime text null
);
