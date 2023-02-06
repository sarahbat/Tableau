with shift_HI as (
	select *,  st_transform(st_setsrid(st_transform(st_translate(geom, 50,6), 5070), 3857), 4326) as geom_albers
	from cb_2021_us_bg_500k_simplified
	where statefp = '15'
),
shift_AK as (
select *,
	st_transform(st_setsrid(st_transform(
		st_rotate(
			st_translate(
				st_scale(
					st_translate(st_transform(geom, 3338), 3900000, -2800000),
					'POINT(0.5 0.5)'
				), 
				2100000,
				-700000
			),
			.6,
			'POINT(3883000 -1300000)'	
			),
			5070), 3857), 4326) as geom_albers	
	from cb_2021_us_bg_500k_simplified
	where statefp = '02'
),
orig_data as (
	select *, st_transform(st_setsrid(st_transform(geom, 5070), 3857), 4326) as geom_albers
	from cb_2021_us_bg_500k_simplified
	where statefp != '02' and statefp != '15' and statefp != '72' and statefp != '66' and statefp != '60' and statefp != '78' and statefp != '69'
)
select *, st_boundary(geom_albers) as geom_albers_outline from orig_data
union all
select *, st_boundary(geom_albers) as geom_albers_outline from shift_ak
union all
select *, st_boundary(geom_albers) as geom_albers_outline from shift_hi
