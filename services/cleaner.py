import pandas as pd
import logging

logger = logging.getLogger(__name__)

class Cleaner:
    def __init__(self):
        pass

    def _use_header_condition_id_make_df(self, documents:list[dict|list])->pd.DataFrame:
        try:
            df = pd.DataFrame(documents)
            return df
        except (KeyError, ValueError, TypeError) as e:
            logger.exception(f"Failed to convert documents to DataFrame: {e}")

    # 製作 jobnane with job_id 的 df
    def _make_jobid_with_jobname(self, original_df:pd.DataFrame) -> pd.DataFrame:
        try:
            cp_ori_df = original_df.copy()

            header_df = pd.json_normalize(cp_ori_df["header"])
            cp_ori_df["job_name"] = header_df["jobName"] 

            job_id_name_df = cp_ori_df[["_id", "job_name"]]

            return job_id_name_df

        except (KeyError, ValueError, TypeError) as e:
            logger.exception(f"Failed to make job_id with job_name DataFrame: {e}")

    # 製作 job_id with skill 的 df 
    def _make_job_skill_or_specialty(self, original_df:pd.DataFrame, skill_or_specialty:str) -> pd.DataFrame:
        purpose = str(skill_or_specialty)

        if purpose not in ["skill", "specialty"]:
            raise ValueError("purpose must be 'skill' or 'specialty'")
        
        try:
            cp_ori_df = original_df[["_id", "condition"]].copy()
            cp_ori_df[purpose] = cp_ori_df["condition"].apply(lambda x: x.get(purpose))


            # 因為 reset index 所以每個 dict 會佔據一 row, 因此對其解 json 後形成的 df 跟 exploded 的 index 相符
            exploded_df = cp_ori_df.explode(purpose).reset_index()

            id_with_purpose_df = exploded_df[["_id", purpose]]

            description_df = pd.json_normalize(id_with_purpose_df[purpose])

            df_final = pd.concat([id_with_purpose_df, description_df], axis=1)
            df_final = df_final.drop(columns=[purpose, "code"])

            return df_final
        except (KeyError, ValueError, TypeError) as e:
            logger.exception(f"Failed to make job_id with {purpose} DataFrame: {e}")