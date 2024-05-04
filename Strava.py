#1. Getting the data  by connecting to the API
creds = with open("creds.txt") as f:
    f.fileread()
client_id = creds[0]
secret = creds[1]

app <- oauth_app("strava", client_id, secret)
endpoint <- oauth_endpoint(
  request = NULL,
  authorize = "https://www.strava.com/oauth/authorize",
  access = "https://www.strava.com/oauth/token"
)

token <- oauth2.0_token(endpoint, app, as_header = FALSE,
                        scope = "activity:read_all")

df_list <- list()
i <- 1
done <- FALSE
while (!done) {
  req <- GET(
    url = "https://www.strava.com/api/v3/athlete/activities",
    config = token,
    query = list(per_page = 200, page = i)
  )
  df_list[[i]] <- fromJSON(content(req, as = "text"), flatten = TRUE)
  if (length(content(req)) < 200) {
    done <- TRUE
  } else {
    i <- i + 1
  }
}

df <- bind_rows(df_list)

#2. Data modification
#This will do some modification on the file and create a data subset focused on triathlon.
df_cleaned <- df %>%
  mutate(Date = as.Date(start_date_local),
         Activity = str_replace_all(type, "Virtual", ""), #Replace virtual ride/run by standard. 
         Activity = fct_lump_min(Activity, 25), #Groups in other all activities done less than 25 times. 
         Distance = distance/1000,
         Time = moving_time/(60*60), #Convert time in hours from seconds
         Speed = Distance/Time
         ) %>%
  subset(select=c(Date, Activity, Distance, Time, Speed))
df_tri <- subset(df_cleaned, Activity=="Run" | Activity=="Swim"|Activity=="Ride")
df_run <- subset(df_cleaned, Activity=="Run")


#3. Aesthetics
#This create a base graph that is used for everything else.
#This first base graph use all data and months. 
base_graph <- ggplot(data=df_cleaned, mapping = aes(x=floor_date(Date, "month"), fill=Activity)) +
  theme_minimal(base_size=9) +
  theme(axis.line = element_line(linewidth = 1), plot.title = element_text(hjust = 0.5), 
        plot.margin = unit(c(0, 0.2, -0.5, 0.5), "lines",), axis.title.y = element_text(angle = 0,vjust = 0.5))+
  xlab("") + 
  ylab("") +
  scale_x_date(date_breaks = "4 month", breaks = "1 month", minor_breaks="1 month", date_labels = "%b\n%Y", 
               expand = c(0, 0)) +
  scale_y_continuous(expand = c(0, 0)) +
  scale_fill_manual(values = c("indianred3", "chartreuse3", "cyan3", "lightsalmon3", "antiquewhite3"), 
                    name = "Type d'activit�",
                    labels=c("V�lo", "Course", "Nage", "Musculation", "Autre")) +
  scale_colour_manual(values = c("indianred3", "chartreuse3", "cyan3", "lightsalmon3", "antiquewhite3"), 
                      name = "Type d'activit�",
                      labels=c("V�lo", "Course", "Nage", "Musculation", "Autre"))


#This base ggraphs gets weekly data for the last 6 months. 
first_value = floor_date(today() %m-% months(6), "month")
last_value = floor_date(today(), "month")-1
timeframe = "week"
base_graph <- ggplot(data=df_cleaned, mapping = aes(x=floor_date(Date, timeframe), fill=Activity, colour=Activity)) +
  theme_minimal(base_size=9) +
  theme(axis.line = element_line(linewidth = 1), plot.title = element_text(hjust = 0.5), 
        plot.margin = unit(c(0, 0.2, -0.5, 0.5), "lines",), axis.title.y = element_text(angle = 0,vjust = 0.5))+
  xlab("") + 
  ylab("") +
  scale_x_date(date_breaks = "1 month", breaks = "1 month", limits= c(first_value, last_value), minor_breaks="1 month", date_labels = "%b\n%Y", 
               expand = c(0, 0)) +
  scale_y_continuous(expand = c(0, 0)) +
  scale_fill_manual(values = c("indianred3", "chartreuse3", "cyan3", "lightsalmon3", "antiquewhite3"), 
                    name = "Type d'activit�",
                    labels=c("V�lo", "Course", "Nage", "Musculation", "Autre")) +
  scale_colour_manual(values = c("indianred3", "chartreuse3", "cyan3", "lightsalmon3", "antiquewhite3"), 
                      name = "Type d'activit�",
                      labels=c("V�lo", "Course", "Nage", "Musculation", "Autre"))


#4. Plot data part 1
#This create 4 plots for 4 interesting y value.
nb_graph <- base_graph + geom_bar() + ggtitle("Quantit�") + ylab("#")
time_graph <- base_graph + geom_col(mapping=aes(y=Time)) + ggtitle("Dur�e")  + ylab("h")
km_graph <- base_graph + geom_col(mapping=aes(y=Distance)) + ggtitle("Distance") + ylab("k\nm")

#I still plot run speed separately
spd_graph <- base_graph + stat_summary(data=df_run, mapping=aes(y=Speed, colour=Activity), linewidth=1.5, geom="line",fun=mean) +
  geom_smooth(data=df_run, mapping=aes(y=Speed), linetype="dashed", fill = "NA") +
  ggtitle("Vitesse") + ylab("k\nm\n/\nh") + scale_colour_manual(values = "chartreuse3", 
                                                              name = "Type d'activit�",
                                                              labels=c("Course"))  

ggarrange(spd_graph, nrow=2, ncol=1, 
          common.legend = TRUE, legend="bottom")
annotate_figure(spd_graph, top = text_grob("Les activit�s sportives de Maxime", hjust=0.5, face="bold", size=16))


#I end up using only 2 value, mostly because 'speed and 'distance' is irrelevant for most of my
#other activities and for weight training. 
plot <- ggarrange(nb_graph, time_graph, nrow=2, ncol=1, 
                  common.legend = TRUE, legend="bottom")
annotate_figure(plot, top = text_grob("Les activit�s sportives cumul�es de Maxime", hjust=0.5, face="bold", size=16))



#5. Plot data part 2
#This is the base to plot a facet element. 
facet_graph <- base_graph + theme(strip.background = element_blank(), strip.text = element_blank()) +
  scale_y_continuous(labels=scales::number_format(accuracy=1), n.breaks=4, expand = c(0, 0)) + 
  facet_grid(vars(Activity[Activity=="Run" | Activity=="Swim"|Activity=="Ride"]), scales="free_y") 

#This creates the 4 facets. The structure is similar to part 1. 
nb_graph2 <- facet_graph + geom_line(data=df_tri, stat="count", linewidth=1.5) + 
  ggtitle("Quantit�") + ylab("#")

time_graph2 <- facet_graph + 
  stat_summary(data=df_tri, mapping=aes(y=Time), linewidth=1.5, geom="line", fun=sum) +
  ggtitle("Dur�e")  + ylab("h")

km_graph2 <- facet_graph + 
  stat_summary(data=df_tri, mapping=aes(y=Distance), linewidth=1.5, geom="line", fun=sum) +
  ggtitle("Distance") + ylab("k\nm")

spd_graph2 <- facet_graph + 
  stat_summary(data=df_tri, mapping=aes(y=Speed), linewidth=1.5, geom="line", fun=mean) +
  geom_smooth(data=df_tri, mapping=aes(y=Speed), linetype="dashed", fill = "NA") + 
  ggtitle("Vitesse") + ylab("k\nm\n/\nh")

#Plotting the result
plot <- ggarrange(nb_graph2, time_graph2, km_graph2, spd_graph2, nrow=2, ncol=2, 
                  common.legend = TRUE, legend="bottom")
annotate_figure(plot, top = text_grob("Les activit�s sportives de Maxime", hjust=0.5, face="bold", size=16))


