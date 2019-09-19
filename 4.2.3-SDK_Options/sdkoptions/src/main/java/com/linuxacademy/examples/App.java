package com.linuxacademy.examples;

import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBMapper;

public class App {

  public static void main(String[] args) {

    AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard().build();

    DynamoDBMapper mapper = new DynamoDBMapper(client);

    MusicItem keySchema = new MusicItem();
    keySchema.setArtist("Queen");
    keySchema.setSongTitle("I Want It All");

    try {
      MusicItem result = mapper.load(keySchema);
      if (result != null) {
        System.out.println("The song was released in " + result.getYear());
      } else {
        System.out.println("No matching song was found");
      }
    } catch (Exception e) {
      System.err.println("Unable to retrieve data: ");
      System.err.println(e.getMessage());
    }

  }

}