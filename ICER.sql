
--- PER PROVINCE PER R-LADDER TREATMENT ---

select R.benchmark_group, sum(amount) from asmfa_flowchain fn
-- select * from asmfa_flowchain fn
    left join asmfa_flow f on fn.id = f.flowchain_id
    left join asmfa_actor dest on f.destination_id = dest.id
    left join asmfa_process p on dest.process_id = p.id
    left join rhierarchy R on R.processing_code =p.code
where fn.dataset_id = 2
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

--- PER PROVINCE PER R-LADDER TREATMENT PER BEST PRACTICE ---


select sum(fc.amount)amount_t, R.r_code current_rank, bt.rank alt_rank
        from asmfa_flowchain fc
            left join asmfa_flow f on fc.id = f.flowchain_id
            left join asmfa_waste06 w on fc.waste06_id = w.id
            left join asmfa_actor orig on f.origin_id = orig.id
--             left join asmfa_company orig_c on orig.company_id = orig_c.id
            left join asmfa_actor dest on f.destination_id = dest.id
--             left join asmfa_company dest_c on dest.company_id = dest_c.id
            left join asmfa_process p on dest.process_id = p.id
            right join rhierarchy R on p.code = R.processing_code
            left join best_treatment bt on w.ewc_code = bt.ewc_code
--             left join processors pcs on (w.ewc_code) = (pcs.ewc_code)
--             where f.origin_role = 'production'
--             and orig.id in
--                   (  select a.id from asmfa_actor a,
--                     (select * from asmfa_area where asmfa_area.name = 'Noord-Holland') NH
--                     where st_contains(NH.geom, a.geom) )

            WHERE fc.dataset_id = 2
--             and R.r_code < pcs.rank
        group by R.r_code, bt.rank;


