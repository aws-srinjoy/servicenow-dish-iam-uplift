extern crate env_logger;

extern crate futures;
extern crate rusoto_core;
extern crate rusoto_iam;
extern crate tokio_core;

extern crate serde_json;

use rusoto_iam::{Iam,IamClient,ListRolesRequest,SimulatePrincipalPolicyRequest};
use rusoto_core::Region;

use std::collections::HashMap;

use std::fs::File;
use std::error::Error;
use std::io::BufReader;
use std::path::Path;
use std::io::Read;

#[tokio::main]
async fn main() {
    println!("Starting");
    let _ = env_logger::try_init();

    /*
    let filename="iam_definition.json";
    let file = File::open(filename).unwrap();
    let reader = BufReader::new(file);
    */
    /*
    let x:serde_json::Value = serde_json::from_reader(File::open("iam_definition.json").unwrap()).expect("Not well formatted");
    let mut access_level_to_actions=HashMap::new();
    let iam_definition=x.as_array().unwrap();
    for service in iam_definition {
        let prefix=service.get("prefix").unwrap().as_str().unwrap();
        //println!("{}",prefix);
        for privilege in service.get("privileges").unwrap().as_array().unwrap() {
            let action=privilege.get("privilege").unwrap().as_str().unwrap();
            let access_level=privilege.get("access_level").unwrap().as_str().unwrap();
            let service_action=format!("{}:{}",prefix,action);
            //println!("{} {} {}",action,access_level,service_action);
            //access_level_to_actions.entry(access_level).or_default().push(service_action);
            access_level_to_actions.entry(access_level).or_insert(Vec::new()).push(service_action);
        }
    }
    */

    /*
    let access_level_to_actions=get_permissions().await;

    for (key,value) in &access_level_to_actions {
      println!("{} {}",key,value.len())
    }
    */

    //run_query("arn:aws:iam::971002977840:role/AwsSecurityAudit".to_string(),access_level_to_actions.get("Permissions management").unwrap().to_vec()).await;

    /*
    let roles=get_all_iam_roles().await;
    for _role in roles {
        println!("{}",_role)
    }
    */

  evaluate_principals().await;
}

async fn get_permissions() -> HashMap<String,Vec<String>> {
    let x:serde_json::Value = serde_json::from_reader(File::open("iam_definition.json").unwrap()).expect("Not well formatted");
    let mut access_level_to_actions=HashMap::new();
    let iam_definition=x.as_array().unwrap();
    for service in iam_definition {
        let prefix=service.get("prefix").unwrap().as_str().unwrap();
        //println!("{}",prefix);
        for privilege in service.get("privileges").unwrap().as_array().unwrap() {
            let action=privilege.get("privilege").unwrap().as_str().unwrap();
            let access_level=privilege.get("access_level").unwrap().as_str().unwrap();
            let service_action=format!("{}:{}",prefix,action);
            //println!("{} {} {}",action,access_level,service_action);
            //access_level_to_actions.entry(access_level).or_default().push(service_action);
            access_level_to_actions.entry(access_level.to_string()).or_insert(Vec::new()).push(service_action);
        }
    }
    return access_level_to_actions
}

async fn get_all_iam_roles() -> Vec<String> {
    let iam_client=IamClient::new(Region::UsEast1);
    let listrolesrequest = ListRolesRequest{max_items: Some(1000), ..Default::default()};

    let mut found_roles:Vec<String>=Default::default();
    println!("Invoking list roles");
    match iam_client.list_roles(listrolesrequest).await {
        Ok(output) => match output.roles {
            roles => {
                println!("Roles found");

                for role in roles {
                    //println!("{} {}",role.role_name,role.arn);
                    found_roles.push(role.arn);
                }
                found_roles
            }
        },
        Err(error) => {
            println!("Error: {:?}", error);
            panic!("Error list roles");
        }
    }
}

async fn query_iam_simulator(principal:String, permissions:Vec<String>) -> Vec<String> {
    let iam_client=IamClient::new(Region::UsEast1);
    let simulateprincipalpolicyrequest=SimulatePrincipalPolicyRequest{policy_source_arn:principal,action_names:permissions, ..Default::default()};

    match iam_client.simulate_principal_policy(simulateprincipalpolicyrequest).await {
        Ok(output) => match output.evaluation_results {
            Some(evaluation_results) => {
                let mut found_actions:Vec<String>=Default::default();
                for evaluation_result in evaluation_results {
                        //println!("{}",evaluation_result.eval_decision);
                        if "allowed"==evaluation_result.eval_decision {
                          found_actions.push(evaluation_result.eval_decision);
                        }
                }
                return found_actions
            }
            None => {
              println!("No simulation evaluation results!");
              Default::default()
            }
        },
        Err(error) => {
            println!("Error: {:?}", error);
            panic!("Error invoking simulate principal policy");
        }
    }
}

async fn run_query(principal:String, permissions:Vec<String>) -> Vec<String> {
  let mut found_actions:Vec<String>=Default::default();
  let chunk_size:usize=125;
  for chunk in permissions.chunks(125) {
    //println!("{:02?}",chunk);
    let actions=query_iam_simulator(principal.as_str().to_string(),chunk.to_vec()).await;
    found_actions.extend(actions);
  }
  return found_actions
}

async fn run_queries(principal:&str,access_level_to_actions:HashMap<String,Vec<String>>) -> HashMap<&str,Vec<String>> {
  let mut found_actions=HashMap::new();

  let permissions_management=access_level_to_actions.get("Permissions management").unwrap().to_vec();
  let actions_m=run_query(principal.to_string(),permissions_management).await;
  found_actions.entry("Permissions management").or_insert(Vec::new()).extend(actions_m);

  let permissions_tagging=access_level_to_actions.get("Tagging").unwrap().to_vec();
  let actions_t=run_query(principal.to_string(),permissions_tagging).await;
  found_actions.entry("Tagging").or_insert(Vec::new()).extend(actions_t);

  let permissions_list=access_level_to_actions.get("List").unwrap().to_vec();
  let actions_l=run_query(principal.to_string(),permissions_list).await;
  found_actions.entry("List").or_insert(Vec::new()).extend(actions_l);

  let permissions_read=access_level_to_actions.get("Read").unwrap().to_vec();
  let actions_r=run_query(principal.to_string(),permissions_read).await;
  found_actions.entry("Read").or_insert(Vec::new()).extend(actions_r);

  let permissions_write=access_level_to_actions.get("Write").unwrap().to_vec();
  let actions_w=run_query(principal.to_string(),permissions_write).await;
  found_actions.entry("Write").or_insert(Vec::new()).extend(actions_w);

  return found_actions
}

async fn evaluate_principals() {
  let access_level_to_actions=get_permissions().await;

  let roles=get_all_iam_roles().await;
  let total_roles=roles.len();
  let mut counter=0;
  for _role in roles {
      //println!("{}",_role)
      let found_actions=run_queries(&_role.to_string(),access_level_to_actions.clone()).await;
      counter+=1;
      if counter%2==0 {
        println!("Completed {} roles out of {}",counter,total_roles);
      }
  }
}
