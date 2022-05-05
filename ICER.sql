
--- PER PROVINCE PER R-LADDER TREATMENT ---

select R.benchmark_group, sum(amount) from asmfa_flowchain fn
-- select * from asmfa_flowchain fn
    left join asmfa_flow f on fn.id = f.flowchain_id
    left join asmfa_actor dest on f.destination_id = dest.id
    left join asmfa_process p on dest.process_id = p.id
    left join asmfa_waste06 w on fn.waste06_id = w.id
    left join rhierarchy R on R.processing_code =p.code
where fn.dataset_id = 2
                and w.materials like '%AbiotischMateriaal%' and w.materials not like '%BiotischMateriaal%'-- Abiotic
--                 and w.materials like '%BiotischMateriaal%' and w.materials not like '%AbiotischMateriaal%'-- Biotic
--                 and (w.materials not like '%iotischMateriaal%' or (w.materials like '%AbiotischMateriaal%' and w.materials like '%BiotischMateriaal%')) -- Mixed
group by R.benchmark_group;


--- BEST POSSIBLE best possible treatment per ewc code
-- drop view best_treatment;
create view best_treatment as
select distinct w.ewc_code, first_value(R.r_code)
                            over (
                                partition by w.ewc_code
                                order by R.r_code)  rank
from asmfa_flowchain fc
left join asmfa_waste06 w on fc.waste06_id = w.id
left join asmfa_flow f on fc.id = f.flowchain_id
left join asmfa_actor a on f.destination_id = a.id
left join asmfa_process p on a.process_id = p.id
right join rhierarchy R on p.code = R.processing_code
where fc.dataset_id = 2;

--- actor id per province it belongs to
-- drop view provinces;
-- create view provinces as
-- select actor.id, area.name from asmfa_actor actor, asmfa_area area
-- where area.adminlevel_id = 8
--       and st_contains(area.geom, actor.geom);

--- PER PROVINCE PER R-LADDER TREATMENT PER BEST PRACTICE ---
select province, sum(fc.amount)amount_t, R.r_code current_rank, bt.rank alt_rank
-- select sum(fc.amount)amount_t
        from asmfa_flowchain fc
            left join asmfa_flow f on fc.id = f.flowchain_id
            left join asmfa_waste06 w on fc.waste06_id = w.id
            left join asmfa_actor orig on f.origin_id = orig.id
            right join
                (select actor.id, area.name province from asmfa_actor actor, asmfa_area area
                    where area.adminlevel_id = 8
                    and st_contains(area.geom, actor.geom)) provinces
                    on orig.id = provinces.id
            left join asmfa_actor dest on f.destination_id = dest.id
            left join asmfa_process p on dest.process_id = p.id
            right join rhierarchy R on p.code = R.processing_code
            left join best_treatment bt on w.ewc_code = bt.ewc_code
            WHERE fc.dataset_id = 2
--                 and w.materials like '%AbiotischMateriaal%' and w.materials not like '%BiotischMateriaal%'-- Abiotic
--                 and w.materials like '%BiotischMateriaal%' and w.materials not like '%AbiotischMateriaal%'-- Biotic
                and (w.materials not like '%iotischMateriaal%' or (w.materials like '%AbiotischMateriaal%' and w.materials like '%BiotischMateriaal%')) -- Mixed
--             and R.r_code < pcs.rank
        group by province, R.r_code, bt.rank;


--- NATIONAL
select sum(fc.amount) amount_t , R.r_code current_rank, bt.rank alt_rank
        from asmfa_flowchain fc
            left join asmfa_flow f on fc.id = f.flowchain_id
            left join asmfa_waste06 w on fc.waste06_id = w.id
            left join asmfa_actor orig on f.origin_id = orig.id
            right join
                (select actor.id, area.name province from asmfa_actor actor, asmfa_area area
                    where area.name = 'Netherlands'
                    and st_contains(area.geom, actor.geom)) in_netherlands
                    on orig.id = in_netherlands.id
            left join asmfa_actor dest on f.destination_id = dest.id
            left join asmfa_process p on dest.process_id = p.id
            right join rhierarchy R on p.code = R.processing_code
            left join best_treatment bt on w.ewc_code = bt.ewc_code
            WHERE fc.dataset_id = 2
--             and R.r_code < pcs.rank
        group by R.r_code, bt.rank;


--- MAP OF BEST PRACTICES ---

-- SELECT a.geom, w.ewc_code, R.r_code
SELECT st_asewkt(a.geom), R.r_code
-- select count(distinct(geom))
from asmfa_actor a
    left join asmfa_flow f on a.id = f.destination_id
    left join asmfa_flowchain fc on f.flowchain_id = fc.id
    left join asmfa_process p on a.process_id = p.id
    left join asmfa_waste06 w on fc.waste06_id = w.id
    right join rhierarchy R on p.code = R.processing_code
    inner join best_treatment bt
        on w.ewc_code = bt.ewc_code
               and R.r_code = bt.rank
WHERE a.dataset_id = 2
and R.r_code <> 'I'
--     and w.materials like '%AbiotischMateriaal%' and w.materials not like '%BiotischMateriaal%'-- Abiotic
--     and w.materials like '%BiotischMateriaal%' and w.materials not like '%AbiotischMateriaal%'-- Biotic
    and (w.materials not like '%iotischMateriaal%' or (w.materials like '%AbiotischMateriaal%' and w.materials like '%BiotischMateriaal%')) -- Mixed
group by a.geom, R.r_code;
