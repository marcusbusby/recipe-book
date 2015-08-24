drop table if exists recipes;
create table recipes (
	e_id integer primary key autoincrement,
	title text not null,
	instructions text not null
);

drop table if exists ingredients;
create table ingredients (
	i_id integer primary key autoincrement,
	ingredient text,
	amount integer,
	e_id integer,
	Foreign Key (e_id) references entry(e_id)
);


